"""Exporta um snapshot agregado, coerente e reproduzivel do PostgreSQL ativo.

Uso no container: python /opt/airflow/project/src/export_dashboard.py
Somente leitura no banco; publica um unico JSON por substituicao atomica.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

MIN_GROUP = 10
NETWORKS = {'1': 'Pública', '2': 'Pública', '3': 'Pública',
            '4': 'Privada com fins lucrativos', '5': 'Privada sem fins lucrativos'}


def number(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(type(value).__name__)


def percent(n, d):
    return round(100 * float(n) / float(d), 4) if d else None


def trajectory_groups(rows, keys):
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in keys)].append(r)
    result = []
    for key, items in sorted(groups.items()):
        denom = sum(r['denominador'] for r in items)
        if denom < MIN_GROUP:
            continue
        counts = {k: sum(r[k] for r in items) for k in
                  ('ingressantes', 'concluintes_acum', 'desistentes_acum', 'permanencia', 'desistentes_ano')}
        assert counts['concluintes_acum'] + counts['desistentes_acum'] + counts['permanencia'] == denom
        result.append(dict(zip(keys, key), cursos=len(items), n=counts['ingressantes'], denominador=denom,
                           tca=percent(counts['concluintes_acum'], denom),
                           tda=percent(counts['desistentes_acum'], denom),
                           tap=percent(counts['permanencia'], denom),
                           tada=percent(counts['desistentes_ano'], denom)))
    return result


def read_snapshot(dsn):
    with psycopg2.connect(dsn) as conn:
        conn.set_session(isolation_level='REPEATABLE READ', readonly=True)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            def q(sql):
                cur.execute(sql)
                return [dict(r) for r in cur.fetchall()]
            sources = q('SELECT a.source_key,d.family,d.source_path,d.rows_loaded,d.sha256,d.version,a.run_id FROM audit.fd_active a JOIN audit.fd_dataset d USING(version) ORDER BY a.source_key')
            trajectory = q('SELECT * FROM core.trajetoria_acumulada_mt ORDER BY coorte,curso,referencia')
            census = q("SELECT * FROM core.censo_mt WHERE nivel='1' ORDER BY ano,curso,municipio")
            indicators = q('SELECT * FROM core.indicadores_mt ORDER BY tipo,ano,entidade')
            labels = q("""SELECT DISTINCT (payload->>'co_curso') curso,
                (payload->>'nu_ano_ingresso')::int coorte,
                payload->>'no_cine_rotulo' rotulo, payload->>'no_cine_area_geral' area,
                payload->>'tp_grau_academico' grau
                FROM staging.fd_raw JOIN audit.fd_active USING(version)
                JOIN audit.fd_dataset USING(version) WHERE family='trajetoria'""")
            lic_raw = q("""SELECT payload->>'codigo_do_curso' curso,
                trim(payload->>'area_de_avaliacao') area,
                payload->>'total_de_concluinte_igual_ou_acima_do_padrao_1_de_proficiencia' proficientes
                FROM staging.fd_raw JOIN audit.fd_active USING(version)
                WHERE source_key='enade_licenciaturas_2025'""")
            quality = q("""SELECT 'Trajetória' fonte,coorte::text periodo,count(*) linhas,
                count(DISTINCT curso) cursos,count(*) FILTER(WHERE cine IS NULL OR municipio IS NULL) campos_ausentes,
                0 excluidos_sequenciais FROM core.trajetoria_mt GROUP BY coorte
                UNION ALL SELECT 'Censo',ano::text,count(*),count(DISTINCT curso),
                count(*) FILTER(WHERE cine IS NULL OR rede IS NULL),count(*) FILTER(WHERE nivel<>'1')
                FROM core.censo_mt GROUP BY ano ORDER BY fonte,periodo""")
            ibge = q('SELECT tabela,status_valor,count(*) linhas FROM core.ibge_mt GROUP BY 1,2 ORDER BY 1,2')
    return sources, trajectory, census, indicators, labels, lic_raw, quality, ibge


def build_snapshot(inputs):
    sources, trajectory, census, indicators, labels, lic_raw, quality, ibge = inputs
    assert len(sources) == 31, 'Catalogo ativo incompleto: esperadas 31 fontes'
    label_map = {(r['curso'], r['coorte']): r for r in labels}
    assert len(label_map) == len(labels), 'Rotulos conflitantes para curso/coorte'
    assert len({(r['curso'], r['coorte'], r['referencia']) for r in trajectory}) == len(trajectory)
    for r in trajectory:
        r.update(label_map[(r['curso'], r['coorte'])])
        assert r['modalidade'] == '1', 'Trajetoria fora do recorte presencial'
        assert r['concluintes_acum'] + r['desistentes_acum'] + r['permanencia'] == r['denominador']
    p1 = trajectory_groups(trajectory, ('coorte', 'referencia'))
    fifth = [r for r in trajectory if r['referencia'] == r['coorte'] + 4]
    p2 = {level: trajectory_groups(fifth, ('coorte', level)) for level in ('rotulo', 'area')}
    # Ofertas/polos consolidados por curso/ano antes dos agregados de rede.
    courses = {}
    ignored_categories = set()
    for r in census:
        if r['categoria'] not in NETWORKS:
            ignored_categories.add(r['categoria'])
            continue
        key = (r['ano'], r['curso'])
        dimensions = (r['modalidade'], NETWORKS[r['categoria']])
        if key not in courses:
            courses[key] = dict(ano=r['ano'], curso=r['curso'], modalidade=dimensions[0], rede=dimensions[1],
                                matriculas=0, desvinculados=0, transferidos=0, ofertas=0)
        row = courses[key]
        assert (row['modalidade'], row['rede']) == dimensions, 'Dimensoes conflitantes entre polos'
        for k in ('matriculas', 'desvinculados', 'transferidos'):
            row[k] += r[k]
        row['ofertas'] += 1
    p3_groups = defaultdict(list)
    for r in courses.values():
        p3_groups[(r['ano'], r['modalidade'], r['rede'])].append(r)
    p3 = []
    for (year, modality, network), rows in sorted(p3_groups.items()):
        totals = {k: sum(r[k] for r in rows) for k in ('matriculas', 'desvinculados', 'transferidos', 'ofertas')}
        denom = sum(totals[k] for k in ('matriculas', 'desvinculados', 'transferidos'))
        if denom >= MIN_GROUP and totals['matriculas'] >= MIN_GROUP:
            p3.append(dict(ano=year, modalidade=modality, rede=network, cursos=len(rows),
                           n=denom, matriculas=totals['matriculas'], proxy=percent(totals['desvinculados'], denom)))
    # Coorte fixa, horizonte fixo: evita comparar turmas em tempos diferentes.
    baseline = {r['curso']: r for r in trajectory if r['coorte'] == 2015 and r['referencia'] == 2024}
    cpc = [r for r in indicators if r['tipo'] == 'cpc']
    assert len({r['curso'] for r in cpc}) == len(cpc), 'CPC duplicado no ciclo: definir criterio antes de juntar'
    joined_cpc = [r for r in cpc if r['curso'] in baseline]
    valid_cpc = [r for r in joined_cpc if r['continuo'] is not None and baseline[r['curso']]['denominador'] >= MIN_GROUP]
    cpc_rows = []
    for r in valid_cpc:
        item = dict(baseline[r['curso']], faixa=str(r['faixa']), cpc=float(r['continuo']))
        cpc_rows.append(item)
    p4 = trajectory_groups(cpc_rows, ('faixa',))
    # Pearson nao ponderado, unidade curso; nao e causal nem ajuste por confundidores.
    x = [r['cpc'] for r in cpc_rows]
    y = [100 * float(r['desistentes_acum']) / float(r['denominador']) for r in cpc_rows]
    correlation = None
    if len(x) > 2:
        mx, my = sum(x)/len(x), sum(y)/len(y)
        ssx, ssy = sum((v-mx)**2 for v in x), sum((v-my)**2 for v in y)
        if ssx and ssy:
            correlation = round(sum((a-mx)*(b-my) for a,b in zip(x,y)) / (ssx*ssy)**0.5, 4)
    lic = [r for r in indicators if r['tipo'] == 'enade_licenciaturas']
    lic_map = {r['curso']: r for r in lic_raw}
    assert len(lic_map) == len(lic_raw) == len(lic)
    lic_matches = [r for r in lic if r['curso'] in baseline and baseline[r['curso']]['grau'] == '2']
    lic_valid = [r for r in lic_matches if r['proficiencia'] is not None and
                 r['participantes'] is not None and r['participantes'] >= MIN_GROUP and
                 baseline[r['curso']]['denominador'] >= MIN_GROUP and
                 lic_map[r['curso']]['proficientes'] not in (None, '', '--')]
    lic_groups = defaultdict(list)
    for r in lic_valid:
        lic_groups[lic_map[r['curso']]['area']].append(r)
    p5 = []
    for area, rows in sorted(lic_groups.items()):
        outcome = trajectory_groups([dict(baseline[r['curso']], area_enade=area) for r in rows], ('area_enade',))[0]
        participants = sum(r['participantes'] for r in rows)
        proficient = sum(int(lic_map[r['curso']]['proficientes']) for r in rows)
        assert 0 <= proficient <= participants
        p5.append(dict(outcome, participantes=participants, proficiencia=percent(proficient, participants)))
    indicator_quality = []
    for typ, year in sorted({(r['tipo'], r['ano']) for r in indicators}):
        rows = [r for r in indicators if (r['tipo'], r['ano']) == (typ, year)]
        metric = 'proficiencia' if typ.startswith('enade_') else 'continuo'
        indicator_quality.append(dict(tipo=typ, ano=year, linhas=len(rows), metrica=metric,
                                      ausentes=sum(r[metric] is None for r in rows)))
    joins = [dict(pergunta='P4', origem=len(cpc), correspondentes=len(joined_cpc), elegiveis=len(cpc_rows),
                  taxa_match=percent(len(joined_cpc), len(cpc)), chave='Código do curso; coorte 2015, referência 2024'),
             dict(pergunta='P5', origem=len(lic), correspondentes=len(lic_matches), elegiveis=len(lic_valid),
                  taxa_match=percent(len(lic_matches), len(lic)), chave='Código do curso e grau licenciatura; coorte 2015, referência 2024')]
    fingerprint = hashlib.sha256(json.dumps(sources, sort_keys=True, default=number).encode()).hexdigest()
    payload = dict(meta=dict(gerado_em=datetime.now(timezone.utc).isoformat(), versao=1,
                            fontes=len(sources), linhas=sum(r['rows_loaded'] for r in sources),
                            lote=sources[0]['run_id'], assinatura= fingerprint, minimo_grupo=MIN_GROUP,
                            categorias_censo_excluidas=sorted(ignored_categories)),
                   fontes=sources, p1=p1, p2=p2, p3=p3, p4=p4, p5=p5,
                   correlacao_cpc=dict(pearson=correlation, cursos=len(cpc_rows), coorte=2015, referencia=2024),
                   qualidade=dict(perfis=quality, indicadores=indicator_quality, ibge=ibge, juncoes=joins,
                                  verificacoes=['31 fontes ativas', 'Chaves de trajetória únicas',
                                                'Contagens da trajetória reconciliadas', 'CPC único por curso no ciclo',
                                                'Dimensões consistentes entre polos', 'Grupos publicados com base >= 10']))
    assert all(r['n'] >= MIN_GROUP for section in (p1, p2['rotulo'], p2['area'], p3, p4, p5) for r in section)
    return payload


def export(destination):
    snapshot = build_snapshot(read_snapshot(os.environ['DATAMIND_DB_DSN']))
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.tmp')
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, default=number, indent=2), encoding='utf-8')
    temporary.replace(destination)
    return dict(arquivo=str(destination), fontes=snapshot['meta']['fontes'],
                linhas=snapshot['meta']['linhas'], juncoes=snapshot['qualidade']['juncoes'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='/opt/airflow/project/published/prototipo/snapshot.json')
    args = parser.parse_args()
    print(json.dumps(export(args.output), ensure_ascii=False))
