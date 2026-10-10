"""Primeiro fluxo analitico: trajetoria 2015 MT. Implementacao do slide 4.

Staging/candidatos por execucao; core/mart imutaveis por versao de fonte+codigo.
A publicacao aponta para uma versao somente depois da validacao.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile

import openpyxl
import psycopg2

ROOT = Path('/opt/airflow/project')
CONTRACT = 'trajetoria_mt_2015_v1'

DDL = '''
CREATE TABLE IF NOT EXISTS audit.trajectory_run (
 run_key text PRIMARY KEY, airflow_run_id text NOT NULL, version text,
 state text NOT NULL, details jsonb NOT NULL DEFAULT '{}',
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS audit.publication (
 product text PRIMARY KEY, version text NOT NULL, run_key text NOT NULL,
 published_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS staging.trajectory_raw (
 run_key text NOT NULL, source_row integer NOT NULL, payload jsonb NOT NULL,
 PRIMARY KEY (run_key, source_row)
);
CREATE TABLE IF NOT EXISTS staging.trajectory_candidate (
 run_key text NOT NULL, co_curso text NOT NULL, co_ies text NOT NULL,
 coorte integer NOT NULL, referencia integer NOT NULL, modalidade text NOT NULL,
 uf text NOT NULL, ingressantes bigint NOT NULL, permanencia bigint NOT NULL,
 concluintes_ano bigint NOT NULL, desistentes_ano bigint NOT NULL, falecidos_ano bigint NOT NULL,
 concluintes_acum bigint NOT NULL, desistentes_acum bigint NOT NULL, falecidos_acum bigint NOT NULL,
 denominador bigint NOT NULL, tap numeric NOT NULL, tca numeric NOT NULL, tda numeric NOT NULL,
 tcan numeric NOT NULL, tada numeric NOT NULL,
 PRIMARY KEY (run_key, co_curso, coorte, referencia)
);
CREATE TABLE IF NOT EXISTS core.trajectory (
 version text NOT NULL, co_curso text NOT NULL, co_ies text NOT NULL,
 coorte integer NOT NULL, referencia integer NOT NULL, modalidade text NOT NULL,
 uf text NOT NULL, ingressantes bigint NOT NULL, permanencia bigint NOT NULL,
 concluintes_ano bigint NOT NULL, desistentes_ano bigint NOT NULL, falecidos_ano bigint NOT NULL,
 concluintes_acum bigint NOT NULL, desistentes_acum bigint NOT NULL, falecidos_acum bigint NOT NULL,
 denominador bigint NOT NULL, tap numeric NOT NULL, tca numeric NOT NULL, tda numeric NOT NULL,
 tcan numeric NOT NULL, tada numeric NOT NULL,
 PRIMARY KEY (version, co_curso, coorte, referencia)
);
CREATE TABLE IF NOT EXISTS mart.p1_trajectory (
 version text NOT NULL, referencia integer NOT NULL, cursos bigint NOT NULL,
 ingressantes bigint NOT NULL, permanencia bigint NOT NULL, concluintes bigint NOT NULL,
 desistentes bigint NOT NULL, falecidos bigint NOT NULL, denominador bigint NOT NULL,
 desistentes_ano bigint NOT NULL, concluintes_ano bigint NOT NULL,
 tap numeric NOT NULL, tca numeric NOT NULL, tda numeric NOT NULL, tada numeric NOT NULL,
 PRIMARY KEY (version, referencia)
);
CREATE OR REPLACE VIEW core.trajectory_active AS
 SELECT c.* FROM core.trajectory c JOIN audit.publication p
 ON p.product='p1_trajetoria_2015' AND p.version=c.version;
CREATE OR REPLACE VIEW mart.p1_trajectory_active AS
 SELECT m.* FROM mart.p1_trajectory m JOIN audit.publication p
 ON p.product='p1_trajetoria_2015' AND p.version=m.version;
'''

# SQL separado para manter janelas explicitas e preservar as taxas publicadas.
TRANSFORM = '''
INSERT INTO staging.trajectory_candidate
WITH typed AS (
 SELECT run_key, payload->>'CO_CURSO' co_curso, payload->>'CO_IES' co_ies,
 (payload->>'NU_ANO_INGRESSO')::int coorte, (payload->>'NU_ANO_REFERENCIA')::int referencia,
 payload->>'TP_MODALIDADE_ENSINO' modalidade, payload->>'CO_UF' uf,
 (payload->>'QT_INGRESSANTE')::bigint ingressantes,
 (payload->>'QT_PERMANENCIA')::bigint permanencia,
 (payload->>'QT_CONCLUINTE')::bigint concluintes_ano,
 (payload->>'QT_DESISTENCIA')::bigint desistentes_ano,
 (payload->>'QT_FALECIDO')::bigint falecidos_ano,
 (payload->>'TAP')::numeric tap, (payload->>'TCA')::numeric tca,
 (payload->>'TDA')::numeric tda, (payload->>'TCAN')::numeric tcan, (payload->>'TADA')::numeric tada
 FROM staging.trajectory_raw WHERE run_key=%s
), accumulated AS (
 SELECT *, sum(concluintes_ano) OVER w concluintes_acum,
 sum(desistentes_ano) OVER w desistentes_acum, sum(falecidos_ano) OVER w falecidos_acum
 FROM typed
 WINDOW w AS (PARTITION BY co_curso,coorte ORDER BY referencia ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
)
SELECT run_key,co_curso,co_ies,coorte,referencia,modalidade,uf,
 ingressantes,permanencia,concluintes_ano,desistentes_ano,falecidos_ano,
 concluintes_acum,desistentes_acum,falecidos_acum,ingressantes-falecidos_acum,
 tap,tca,tda,tcan,tada FROM accumulated;
'''

def connection():
    return psycopg2.connect(os.environ['DATAMIND_DB_DSN'])

def status(run_key, state, details):
    with connection() as conn, conn.cursor() as cur:
        cur.execute('UPDATE audit.trajectory_run SET state=%s,details=%s::jsonb,updated_at=now() WHERE run_key=%s',
                    (state,json.dumps(details,ensure_ascii=False),run_key))

def extract(run_id):
    run_key=hashlib.sha256(run_id.encode()).hexdigest()[:24]
    folder=ROOT/'work'/run_key
    folder.mkdir(parents=True,exist_ok=True)
    with connection() as conn,conn.cursor() as cur:
        cur.execute(DDL)
        cur.execute('''INSERT INTO audit.trajectory_run(run_key,airflow_run_id,state) VALUES (%s,%s,'extracting')
            ON CONFLICT(run_key) DO UPDATE SET state='extracting',updated_at=now()''',(run_key,run_id))
    try:
        manifest=json.loads((ROOT/'evidence/manifesto.json').read_text(encoding='utf-8'))
        source=next(x for x in manifest if x['key']=='trajetoria2015')
        path=ROOT/'data/raw'/source['name']
        with path.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
        if digest!=source['sha256'] or path.stat().st_size!=source['bytes']:
            raise ValueError('Arquivo difere do manifesto aprovado')
        code_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        version=hashlib.sha256((digest+CONTRACT+code_hash).encode()).hexdigest()
        with ZipFile(path) as z:
            names=[n for n in z.namelist() if n.lower().endswith('.xlsx') and not Path(n).name.startswith('~')]
            if len(names)!=1: raise ValueError('Esperado um XLSX principal no ZIP')
            import shutil
            with z.open(names[0]) as src,(folder/'source.xlsx').open('wb') as dst:shutil.copyfileobj(src,dst)
        wb=openpyxl.load_workbook(folder/'source.xlsx',read_only=True,data_only=True)
        rows=wb['INDICADORES_TRAJETORIA'].iter_rows(min_row=9,values_only=True)
        headers=[str(x).strip() for x in next(rows)]
        required=['CO_CURSO','CO_IES','CO_UF','TP_MODALIDADE_ENSINO','NU_ANO_INGRESSO','NU_ANO_REFERENCIA',
                  'QT_INGRESSANTE','QT_PERMANENCIA','QT_CONCLUINTE','QT_DESISTENCIA','QT_FALECIDO','TAP','TCA','TDA','TCAN','TADA']
        if not set(required)<=set(headers):raise ValueError('Leiaute incompativel')
        count=0
        with (folder/'staging.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.writer(f)
            for rownum,row in enumerate(rows,start=10):
                d=dict(zip(headers,row))
                if d.get('CO_UF')!=51 or d.get('TP_MODALIDADE_ENSINO')!=1:continue
                if d.get('NU_ANO_INGRESSO')!=2015:raise ValueError('Coorte inesperada')
                if any(d.get(k) is None for k in required):raise ValueError(f'Campo obrigatorio vazio na linha {rownum}')
                # Identificadores numericos integrais do Excel sao canonicalizados para texto.
                for k in ['CO_CURSO','CO_IES','CO_UF','CO_MUNICIPIO','CO_REGIAO']:
                    v=d.get(k)
                    if isinstance(v,(int,float)) and float(v).is_integer():d[k]=str(int(v))
                writer.writerow([run_key,rownum,json.dumps(d,ensure_ascii=False)])
                count+=1
        wb.close()
        if count!=5150:raise ValueError(f'Esperadas 5150 linhas no arquivo fixado; encontradas {count}')
        context={'run_key':run_key,'version':version,'rows':count,'source_hash':digest,'source_url':source['source']}
        (folder/'context.json').write_text(json.dumps(context),encoding='utf-8')
        with connection() as conn,conn.cursor() as cur:
            cur.execute('UPDATE audit.trajectory_run SET version=%s WHERE run_key=%s',(version,run_key))
        status(run_key,'extracted',context)
        return context
    except Exception as exc:
        status(run_key,'quarantined',{'stage':'extract','reason':str(exc)})
        raise

def load(context):
    key=context['run_key']
    with connection() as conn,conn.cursor() as cur:
        cur.execute('DELETE FROM staging.trajectory_raw WHERE run_key=%s',(key,))
        with (ROOT/'work'/key/'staging.csv').open(encoding='utf-8') as f:
            cur.copy_expert('COPY staging.trajectory_raw(run_key,source_row,payload) FROM STDIN WITH (FORMAT CSV)',f)
        cur.execute('SELECT count(*) FROM staging.trajectory_raw WHERE run_key=%s',(key,))
        if cur.fetchone()[0]!=context['rows']:raise ValueError('Contagem staging divergiu')
    status(key,'loaded',context)

def transform(context):
    key=context['run_key']
    with connection() as conn,conn.cursor() as cur:
        cur.execute('DELETE FROM staging.trajectory_candidate WHERE run_key=%s',(key,))
        cur.execute(TRANSFORM,(key,))
    status(key,'transformed',context)

def validate(context, force_failure=False):
    key=context['run_key']
    with connection() as conn,conn.cursor() as cur:
        cur.execute('''SELECT count(*),count(DISTINCT co_curso),
          count(*) FILTER (WHERE uf<>'51' OR modalidade<>'1' OR coorte<>2015 OR referencia NOT BETWEEN 2015 AND 2024),
          count(*) FILTER (WHERE least(ingressantes,permanencia,concluintes_ano,desistentes_ano,falecidos_ano)<0 OR denominador<=0),
          count(*) FILTER (WHERE ingressantes<>permanencia+concluintes_acum+desistentes_acum+falecidos_acum),
          count(*) FILTER (WHERE greatest(
            abs(tap-100.0*permanencia/nullif(denominador,0)),
            abs(tca-100.0*concluintes_acum/nullif(denominador,0)),
            abs(tda-100.0*desistentes_acum/nullif(denominador,0)),
            abs(tcan-100.0*concluintes_ano/nullif(denominador,0)),
            abs(tada-100.0*desistentes_ano/nullif(denominador,0)))>0.000001)
          FROM staging.trajectory_candidate WHERE run_key=%s''',(key,))
        counts=cur.fetchone()
        cur.execute('''SELECT count(*) FROM (SELECT co_curso FROM staging.trajectory_candidate WHERE run_key=%s
            GROUP BY co_curso HAVING count(*)<>10 OR count(DISTINCT referencia)<>10
            OR min(ingressantes)<>max(ingressantes)) x''',(key,))
        series_bad=cur.fetchone()[0]
    result={'rows':counts[0],'courses':counts[1],'invalid_scope':counts[2],'invalid_counts':counts[3],
            'balance_failures':counts[4],'rate_failures':counts[5],'incomplete_series':series_bad,
            'forced_failure_test':force_failure}
    result['valid']=counts[:2]==(5150,515) and all(x==0 for x in counts[2:]) and series_bad==0 and not force_failure
    status(key,'validated' if result['valid'] else 'validation_failed',result)
    return result

def quarantine(context,checks):
    status(context['run_key'],'quarantined',checks)
    return {'published':False,'reason':'Validacao reprovada; publicacao anterior preservada'}

def publish(context,checks):
    if not checks['valid']:raise ValueError('Publicacao sem validacao')
    version,key=context['version'],context['run_key']
    public_dir=ROOT/'published'/'versions'/version
    public_dir.mkdir(parents=True,exist_ok=True)
    with connection() as conn,conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('p1_trajetoria_2015'))")
        cur.execute('''INSERT INTO core.trajectory SELECT %s,co_curso,co_ies,coorte,referencia,modalidade,uf,
            ingressantes,permanencia,concluintes_ano,desistentes_ano,falecidos_ano,
            concluintes_acum,desistentes_acum,falecidos_acum,denominador,tap,tca,tda,tcan,tada
            FROM staging.trajectory_candidate WHERE run_key=%s ON CONFLICT DO NOTHING''',(version,key))
        cur.execute('''INSERT INTO mart.p1_trajectory
            SELECT version,referencia,count(*),sum(ingressantes),sum(permanencia),sum(concluintes_acum),
            sum(desistentes_acum),sum(falecidos_acum),sum(denominador),sum(desistentes_ano),sum(concluintes_ano),
            100.0*sum(permanencia)/sum(denominador),100.0*sum(concluintes_acum)/sum(denominador),
            100.0*sum(desistentes_acum)/sum(denominador),100.0*sum(desistentes_ano)/sum(denominador)
            FROM core.trajectory WHERE version=%s GROUP BY version,referencia ON CONFLICT DO NOTHING''',(version,))
        cur.execute('SELECT * FROM mart.p1_trajectory WHERE version=%s ORDER BY referencia',(version,))
        names=[x.name for x in cur.description]; rows=[dict(zip(names,r)) for r in cur.fetchall()]
        if len(rows)!=10 or any(r['cursos']!=515 for r in rows):raise ValueError('Mart incompleto')
        # Apenas agregado estadual; pequenas contagens subjacentes suprimem medidas da referencia.
        export=[]
        for r in rows:
            suppress=any(0<r[k]<10 for k in ['permanencia','concluintes','desistentes','falecidos','desistentes_ano','concluintes_ano'])
            out={'ano_referencia':r['referencia'],'ano_curso':r['referencia']-2014,'cursos':r['cursos'],
                 'ingressantes':r['ingressantes'],'suprimido':suppress}
            for field in ['tap','tca','tda','tada']:
                out[field]=None if suppress else round(float(r[field]),4)
            export.append(out)
        result={'version':version,'coorte':2015,'uf':'MT','modalidade':'Presencial','source':context['source_url'],
                'method':'Taxas pelas contagens; denominador ingressantes menos falecidos acumulados; percentuais 0-100.',
                'suppression':'Medidas de referencias com contagens positivas inferiores a 10 sao omitidas.',
                'rows':export}
        payload=json.dumps(result,ensure_ascii=False,indent=2).encode()
        target=public_dir/'p1_trajetoria_2015.json'
        temp=public_dir/'p1.tmp';temp.write_bytes(payload);os.replace(temp,target)
        digest=hashlib.sha256(payload).hexdigest()
        cur.execute('''INSERT INTO audit.publication(product,version,run_key) VALUES ('p1_trajetoria_2015',%s,%s)
            ON CONFLICT(product) DO UPDATE SET version=EXCLUDED.version,run_key=EXCLUDED.run_key,published_at=now()''',(version,key))
        cur.execute('UPDATE audit.trajectory_run SET state=%s,details=%s::jsonb,updated_at=now() WHERE run_key=%s',
                    ('published',json.dumps({'checks':checks,'export_sha256':digest}),key))
    # O ponteiro do arquivo avanca somente depois do commit. Retry repara falha nesta ultima etapa.
    pointer={'version':version,'path':f'versions/{version}/p1_trajetoria_2015.json','sha256':digest}
    tmp=ROOT/'published'/'current.tmp';tmp.write_text(json.dumps(pointer,indent=2),encoding='utf-8')
    os.replace(tmp,ROOT/'published'/'current.json')
    return {'version':version,'core_rows':5150,'mart_rows':10,'export_sha256':digest}

def execute(stage,context=None,**kwargs):
    try:
        return globals()[stage](context,**kwargs)
    except Exception as exc:
        if isinstance(context,dict):status(context['run_key'],'quarantined',{'stage':stage,'reason':str(exc)})
        raise
