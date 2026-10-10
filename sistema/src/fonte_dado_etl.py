"""ETL local completo de fonteDado. Staging e core versionados; lote publicado atomicamente."""
import csv
import hashlib
import io
import json
import os
import re
import shutil
import unicodedata
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zipfile import ZipFile

import openpyxl
import psycopg2
from psycopg2 import sql

ROOT = Path(os.environ.get('DATAMIND_PROJECT_ROOT', '/opt/airflow/project'))
SOURCE = ROOT/'fonteDado'
WORK = ROOT/'work'/'fonte_dado'
TABLES = {'trajetoria':'fd_trajetoria','censo':'fd_censo','indicador':'fd_indicador','ibge':'fd_ibge'}
NULLS = {'', 'SC', 'S/C', '-', '--', 'NA', 'N/A', 'NAN', '*', 'NC'}
EXPECTED = ({f'trajetoria_{y}' for y in range(2015,2021)} |
            {f'censo_{y}' for y in range(2021,2025)} |
            {f'{t}_{y}' for t in ['cpc','enade','idd','igc'] for y in range(2021,2024)} |
            {'enade_licenciaturas_2025','enade_medicina_2025'} |
            {f'ibge_{t}' for t in ['10056','10059','10061','10296','5938','6579','9514']})

@contextmanager
def database():
    conn = psycopg2.connect(os.environ['DATAMIND_DB_DSN'])
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()

def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def dumps(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str)

def norm(value):
    s=str(value or '').replace('º','o')
    s=re.sub(r'[*¹²³]','',s)
    return re.sub(r'[^a-z0-9]+','_', ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))).strip('_')

def identifier(value, required=True):
    if value is None or str(value).strip()=='':
        if required:raise ValueError('Identificador obrigatorio vazio')
        return None
    if isinstance(value,(int,float,Decimal)):
        n=Decimal(str(value))
        if not n.is_finite() or n!=n.to_integral_value():raise ValueError(f'Identificador nao integral: {value}')
        return str(int(n))
    return str(value).strip()

def number(value, required=False, integer=False):
    s=str(value).strip() if value is not None else ''
    if s.upper() in NULLS:
        if required:raise ValueError(f'Numero obrigatorio ausente: {s}')
        return None
    if ',' in s:s=s.replace('.','').replace(',','.')
    try:n=Decimal(s)
    except InvalidOperation as exc:raise ValueError(f'Numero invalido: {s}') from exc
    if not n.is_finite():raise ValueError(f'Numero nao finito: {s}')
    if integer:
        if n!=n.to_integral_value():raise ValueError(f'Contagem fracionaria: {s}')
        return int(n)
    return n

def classify(name):
    name=Path(name).name.lower()
    m=re.fullmatch(r'indicadores_trajetoria_es_(201[5-9]|2020)_2024.zip',name)
    if m:return f'trajetoria_{m[1]}','trajetoria',m[1]
    m=re.fullmatch(r'microdados_censo_da_educacao_superior_(202[1-4]).zip',name)
    if m:return f'censo_{m[1]}','censo',m[1]
    m=re.fullmatch(r'tabela_(\d+)_mt.csv',name)
    if m:return f'ibge_{m[1]}','ibge',m[1]
    m=re.fullmatch(r'(cpc|idd|igc)_(202[1-3]).xlsx',name)
    if m:return f'{m[1]}_{m[2]}','indicador',m[2]
    m=re.fullmatch(r'conceito_enade_(202[1-3]).xlsx',name)
    if m:return f'enade_{m[1]}','indicador',m[1]
    if name=='conceito_enade_licenciaturas.xlsx':return 'enade_licenciaturas_2025','indicador','2025'
    if name=='conceito_enade_medicina_2025.xlsx':return 'enade_medicina_2025','indicador','2025'
    return None

def initialize():
    WORK.mkdir(parents=True,exist_ok=True)
    with database() as cur:cur.execute((ROOT/'sql/init/002_fonte_dado.sql').read_text(encoding='utf-8-sig'))

def discover(run_id):
    initialize()
    candidates={}
    for p in sorted(SOURCE.rglob('*')):
        if not p.is_file():continue
        classified=classify(p.name)
        if not classified:continue
        key,family,period=classified
        h=digest(p)
        if key in candidates and candidates[key]['sha256']!=h:raise ValueError(f'Fontes conflitantes para {key}')
        candidates[key]={'key':key,'family':family,'period':period,'path':str(p),'origin':str(p.relative_to(SOURCE)),'sha256':h}
    # Pacotes externos sao fallback. XLSX/CSV ja extraidos tem preferencia sobre ODS/JSON equivalentes.
    for outer in sorted(SOURCE.glob('*.zip')):
        with ZipFile(outer) as z:
            for member in z.namelist():
                classified=classify(member)
                if not classified or classified[0] in candidates:continue
                key,family,period=classified
                folder=WORK/'source_cache'/digest(outer)
                folder.mkdir(parents=True,exist_ok=True)
                path=folder/Path(member).name
                # Reextracao assegura que o cache nao mascara uma alteracao local.
                temp=path.with_suffix('.tmp')
                with z.open(member) as src,temp.open('wb') as dst:shutil.copyfileobj(src,dst)
                os.replace(temp,path)
                candidates[key]={'key':key,'family':family,'period':period,'path':str(path),
                                 'origin':str(outer.relative_to(SOURCE))+'!'+member,'sha256':digest(path)}
    if set(candidates)!=EXPECTED:raise ValueError(f'Catalogo incompleto: faltantes={sorted(EXPECTED-set(candidates))}; extras={sorted(set(candidates)-EXPECTED)}')
    code=digest(Path(__file__)) + digest(ROOT/'sql/init/002_fonte_dado.sql')
    result=[]
    for key,item in sorted(candidates.items()):
        item['version']=hashlib.sha256((key+item['sha256']+code).encode()).hexdigest()
        item['run_id']=run_id
        result.append(item)
    with database() as cur:
        cur.execute("INSERT INTO audit.fd_batch(run_id,state,manifest) VALUES (%s,'loading',%s::jsonb) ON CONFLICT(run_id) DO UPDATE SET state='loading',manifest=EXCLUDED.manifest,updated_at=now()",(run_id,dumps(result)))
    return result

def spreadsheet_rows(path, trajectory=False):
    wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
    try:
        for sheet in wb.worksheets:
            it=sheet.iter_rows(values_only=True)
            for rownum,row in enumerate(it,1):
                names=[norm(v) for v in row]
                required={'co_curso','nu_ano_ingresso','co_uf'} if trajectory else {'ano','codigo_da_ies','sigla_da_uf'}
                if required<=set(names):
                    populated=[n for n in names if n]
                    if len(populated)!=len(set(populated)):raise ValueError('Cabecalhos duplicados')
                    for n,values in enumerate(it,rownum+1):
                        yield n,{k:v for k,v in zip(names,values) if k}
                    return
                if rownum>=20:break
        raise ValueError(f'Cabecalho de dados nao encontrado: {Path(path).name}')
    finally:wb.close()

def csv_rows(stream):
    reader=csv.DictReader(stream,delimiter=';')
    if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):raise ValueError('Cabecalho CSV invalido')
    for n,row in enumerate(reader,2):
        if None in row or any(v is None for v in row.values()):raise ValueError(f'Leiaute CSV irregular na linha {n}')
        yield n,row

def rows(item):
    path=Path(item['path'])
    if item['family']=='trajetoria':
        with ZipFile(path) as z:
            members=[m for m in z.namelist() if m.lower().endswith('.xlsx')]
            if len(members)!=1:raise ValueError('ZIP de trajetoria sem XLSX unico')
            target=WORK/item['version']/'source.xlsx'
            with z.open(members[0]) as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
        yield from spreadsheet_rows(target,True)
    elif item['family']=='censo':
        with ZipFile(path) as z:
            members=[m for m in z.namelist() if 'microdados_cadastro_cursos' in m.lower() and m.lower().endswith('.csv')]
            if len(members)!=1:raise ValueError('Cadastro de cursos ausente ou ambiguo')
            with z.open(members[0]) as raw,io.TextIOWrapper(raw,encoding='cp1252',newline='') as f:yield from csv_rows(f)
    elif item['family']=='indicador':yield from spreadsheet_rows(path)
    else:
        with path.open(encoding='utf-8-sig',newline='') as f:yield from csv_rows(f)

def transform_row(item,d):
    family=item['family'];version=item['version']
    if family=='trajetoria':
        if identifier(d.get('co_uf'),False)!='51':return None
        coorte=number(d['nu_ano_ingresso'],True,True);ref=number(d['nu_ano_referencia'],True,True)
        if coorte!=int(item['period']) or not coorte<=ref<=2024:raise ValueError('Coorte/referencia inesperada')
        return [version,identifier(d['co_curso']),identifier(d['co_ies']),coorte,ref,
                identifier(d.get('co_municipio'),False),identifier(d['tp_modalidade_ensino']),identifier(d['tp_categoria_administrativa']),
                identifier(d.get('co_cine_rotulo'),False),identifier(d.get('co_cine_area_geral'),False),d.get('no_curso'),
                *[number(d[k],True,True) for k in ['qt_ingressante','qt_permanencia','qt_concluinte','qt_desistencia','qt_falecido']],
                *[number(d[k],True) for k in ['tap','tca','tda','tcan','tada']]]
    if family=='censo':
        if d.get('CO_UF')!='51':return None
        year=number(d['NU_ANO_CENSO'],True,True)
        if year!=int(item['period']):raise ValueError('Ano do Censo difere do arquivo')
        measures={k:number(v,False,True) for k,v in d.items() if k.startswith('QT_')}
        if any(v is not None and v<0 for v in measures.values()):raise ValueError('Contagem negativa no Censo')
        return [version,year,identifier(d['CO_CURSO']),identifier(d['CO_IES']),identifier(d['CO_MUNICIPIO']),
                identifier(d['TP_MODALIDADE_ENSINO']),identifier(d['TP_NIVEL_ACADEMICO']),identifier(d['TP_CATEGORIA_ADMINISTRATIVA']),
                identifier(d.get('TP_REDE'),False),identifier(d.get('CO_CINE_ROTULO'),False),d['NO_CURSO'],
                *[number(d[k],True,True) for k in ['QT_MAT','QT_ING','QT_CONC','QT_SIT_DESVINCULADO','QT_SIT_TRANSFERIDO','QT_VG_TOTAL']],
                measures.get('QT_ING_FINANC'),dumps(measures)]
    if family=='indicador':
        if str(d.get('sigla_da_uf','')).strip().upper()!='MT':return None
        year=number(d['ano'],True,True)
        if year!=int(item['period']):raise ValueError('Ano do indicador difere do arquivo')
        kind=item['key'].rsplit('_',1)[0];course=identifier(d.get('codigo_do_curso'),kind!='igc');ies=identifier(d['codigo_da_ies'])
        base='conceito_enade' if kind.startswith('enade') else kind
        raw=d.get(base+'_continuo');continuous=number(raw)
        band=identifier(d.get(base+'_faixa'),False)
        profkey=next((k for k in d if k.startswith('percentual') and 'proficiencia' in k),None)
        if kind=='enade_medicina':profkey='percentual_concluintes_acima_do_padrao'
        prof=number(d.get(profkey)) if profkey else None
        reason=None
        if continuous is None:
            reason='metrica_nao_oferecida' if base+'_continuo' not in d else ('sem_conceito' if str(band).upper()=='SC' else 'ausente_na_fonte')
        return [version,kind,year,ies if kind=='igc' else course,course,ies,identifier(d.get('codigo_do_municipio'),False),
                d.get('modalidade_de_ensino'),d.get('categoria_administrativa'),continuous,band,
                number(d.get('no_de_concluintes_inscritos'),False,True),number(d.get('no_de_concluintes_participantes'),False,True),prof,reason]
    # SIDRA: '-' significa zero absoluto, nunca ausencia; preserva simbolo e unidade.
    level=d['nivel_geografico'];local=d['localidade_id']
    if not ((level=='N3' and local=='51') or (level=='N6' and len(local)==7 and local.startswith('51'))):raise ValueError('Localidade fora de MT')
    if d['tabela']!=item['period']:raise ValueError('Tabela IBGE inesperada')
    categories={k:v for k,v in d.items() if k.startswith('class_') and k.endswith('_id')}
    labels={k:v for k,v in d.items() if k.startswith('class_') and k.endswith('_nome')}
    key=hashlib.sha256(dumps([d['tabela'],d['variavel_id'],d['unidade'],level,local,d['periodo'],categories]).encode()).hexdigest()
    original=d['valor'].strip()
    statuses={'-':'zero_absoluto','...':'nao_disponivel','..':'nao_aplicavel','X':'inibido','':'ausente'}
    status=statuses.get(original,'numerico')
    value=Decimal(0) if original=='-' else (None if original in statuses else number(original,True))
    return [version,key,d['tabela'],d['variavel_id'],d['variavel_nome'],d['unidade'],level,local,d['localidade_nome'],d['periodo'],value,original,status,dumps(categories),dumps(labels)]

def check_source(cur,item,count):
    table=TABLES[item['family']]
    cur.execute(sql.SQL('SELECT count(*) FROM core.{} WHERE version=%s').format(sql.Identifier(table)),(item['version'],))
    if cur.fetchone()[0]!=count or count==0:raise ValueError('Contagem core nao confere')
    cur.execute('SELECT count(*) FROM staging.fd_raw WHERE version=%s',(item['version'],))
    if cur.fetchone()[0]!=count:raise ValueError('Contagem staging nao confere')
    if item['family']=='trajetoria':
        cur.execute('''WITH q AS (SELECT *,sum(concluintes_ano) OVER w c,sum(desistentes_ano) OVER w d,sum(falecidos_ano) OVER w f
         FROM core.fd_trajetoria WHERE version=%s WINDOW w AS (PARTITION BY curso,coorte ORDER BY referencia ROWS UNBOUNDED PRECEDING))
         SELECT count(*) FROM q WHERE ingressantes<>permanencia+c+d+f OR ingressantes-f<=0
         OR greatest(abs(tap-100.0*permanencia/nullif(ingressantes-f,0)),abs(tca-100.0*c/nullif(ingressantes-f,0)),
          abs(tda-100.0*d/nullif(ingressantes-f,0)),abs(tcan-100.0*concluintes_ano/nullif(ingressantes-f,0)),
          abs(tada-100.0*desistentes_ano/nullif(ingressantes-f,0)))>0.000001''',(item['version'],))
        if cur.fetchone()[0]:raise ValueError('Saldo ou taxas da trajetoria nao reconciliam')
        cur.execute('''SELECT count(*) FROM (SELECT curso,coorte FROM core.fd_trajetoria WHERE version=%s
         GROUP BY curso,coorte HAVING count(*)<>2025-coorte OR min(referencia)<>coorte OR max(referencia)<>2024
         OR min(ingressantes)<>max(ingressantes)) q''',(item['version'],))
        if cur.fetchone()[0]:raise ValueError('Serie de trajetoria incompleta')

def process_source(item):
    version=item['version'];folder=WORK/version;folder.mkdir(parents=True,exist_ok=True)
    if digest(item['path'])!=item['sha256']:raise ValueError('Fonte alterada depois do inventario')
    with database() as cur:
        cur.execute('SELECT rows_loaded FROM audit.fd_dataset WHERE version=%s AND state=%s',(version,'ready'))
        cached=cur.fetchone()
        if cached:
            check_source(cur,item,cached[0])
            return {'key':item['key'],'version':version,'rows':cached[0],'cached':True}
        cur.execute('''INSERT INTO audit.fd_dataset(version,source_key,family,source_path,sha256,state)
         VALUES (%s,%s,%s,%s,%s,'loading') ON CONFLICT(version) DO UPDATE SET state='loading',updated_at=now()''',
         (version,item['key'],item['family'],item['origin'],item['sha256']))
    scanned=count=0
    try:
        with (folder/'raw.csv').open('w',encoding='utf-8',newline='') as rf,(folder/'core.csv').open('w',encoding='utf-8',newline='') as cf:
            rw=csv.writer(rf);cw=csv.writer(cf)
            for rownum,raw in rows(item):
                scanned+=1
                converted=transform_row(item,raw)
                if converted is None:continue
                rw.writerow([version,rownum,dumps(raw)])
                # NULL explicito distinto de strings vazias na carga CSV.
                cw.writerow(['\\N' if v is None else v for v in converted])
                count+=1
        with database() as cur:
            cur.execute('SELECT pg_advisory_xact_lock(hashtext(%s))',(item['key'],))
            cur.execute('DELETE FROM staging.fd_raw WHERE version=%s',(version,))
            cur.execute(sql.SQL('DELETE FROM core.{} WHERE version=%s').format(sql.Identifier(TABLES[item['family']])),(version,))
            with (folder/'raw.csv').open(encoding='utf-8') as f:cur.copy_expert('COPY staging.fd_raw FROM STDIN WITH(FORMAT CSV)',f)
            with (folder/'core.csv').open(encoding='utf-8') as f:
                statement=sql.SQL("COPY core.{} FROM STDIN WITH(FORMAT CSV,NULL '\\N')").format(sql.Identifier(TABLES[item['family']]))
                cur.copy_expert(statement.as_string(cur),f)
            check_source(cur,item,count)
            cur.execute("UPDATE audit.fd_dataset SET state='ready',rows_loaded=%s,details=%s::jsonb,updated_at=now() WHERE version=%s",
                        (count,dumps({'scanned':scanned,'selected_mt':count,'excluded':scanned-count}),version))
        return {'key':item['key'],'version':version,'rows':count,'cached':False}
    except Exception as exc:
        with database() as cur:
            cur.execute("UPDATE audit.fd_dataset SET state='quarantined',details=%s::jsonb,updated_at=now() WHERE version=%s",(dumps({'error':str(exc),'scanned':scanned,'selected':count}),version))
            cur.execute("UPDATE audit.fd_batch SET state='quarantined',details=%s::jsonb,updated_at=now() WHERE run_id=%s",(dumps({'source':item['key'],'error':str(exc)}),item['run_id']))
        raise

def publish(results,run_id,force_failure=False):
    results=list(results)
    if force_failure:
        with database() as cur:cur.execute("UPDATE audit.fd_batch SET state='quarantined',details=%s::jsonb,updated_at=now() WHERE run_id=%s",(dumps({'forced_failure_test':True}),run_id))
        raise ValueError('Reprovacao simulada: publicacao anterior preservada')
    if len(results)!=len(EXPECTED) or {r['key'] for r in results}!=EXPECTED:raise ValueError('Lote incompleto')
    with database() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('fonte_dado_publish'))")
        cur.execute("SELECT version FROM audit.fd_dataset WHERE version=ANY(%s) AND state='ready'",([r['version'] for r in results],))
        if len(cur.fetchall())!=len(results):raise ValueError('Fonte ainda nao validada')
        cur.execute('DELETE FROM audit.fd_active')
        cur.executemany('INSERT INTO audit.fd_active(source_key,version,run_id) VALUES (%s,%s,%s)',[(r['key'],r['version'],run_id) for r in results])
        cur.execute("UPDATE audit.fd_batch SET state='published',details=%s::jsonb,updated_at=now() WHERE run_id=%s",(dumps({'datasets':len(results),'rows':sum(r['rows'] for r in results)}),run_id))
    return {'datasets':len(results),'rows':sum(r['rows'] for r in results),'cached':sum(r['cached'] for r in results)}
