"""Valida fontes e conectividade. Nao e o ETL analitico P1-P5."""
from datetime import datetime, timedelta, timezone
from airflow.sdk import dag, task

@dag(
    dag_id='datamind_validar_ambiente',
    description='Confere SHA-256 das cinco fontes e registra manifesto no banco analitico.',
    schedule=None,
    start_date=datetime(2026,10,10,tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args={'retries':1,'retry_delay':timedelta(seconds=10)},
    tags=['datamind','ambiente','fase1'],
)
def environment_dag():
    @task
    def validar_fontes():
        import hashlib,json
        from pathlib import Path
        root=Path('/opt/airflow/project')
        items=json.loads((root/'evidence/manifesto.json').read_text(encoding='utf-8'))
        for item in items:
            path=root/'data/raw'/item['name']
            with path.open('rb') as stream:
                digest=hashlib.file_digest(stream,'sha256').hexdigest()
            if digest != item['sha256'] or path.stat().st_size != item['bytes']:
                raise ValueError('Fonte alterada: '+item['name'])
        return len(items)

    @task
    def registrar_manifesto(expected):
        import json,os
        from pathlib import Path
        import psycopg2
        items=json.loads(Path('/opt/airflow/project/evidence/manifesto.json').read_text(encoding='utf-8'))
        with psycopg2.connect(os.environ['DATAMIND_DB_DSN']) as conn:
            with conn.cursor() as cursor:
                for item in items:
                    cursor.execute('''INSERT INTO audit.source_file
                        (source_key,filename,sha256,bytes,source_url) VALUES (%s,%s,%s,%s,%s)
                        ON CONFLICT (source_key) DO UPDATE SET filename=EXCLUDED.filename,
                        sha256=EXCLUDED.sha256, bytes=EXCLUDED.bytes, source_url=EXCLUDED.source_url''',
                        (item['key'],item['name'],item['sha256'],item['bytes'],item['source']))
                cursor.execute('SELECT count(*) FROM audit.source_file WHERE source_key=ANY(%s)',
                               ([item['key'] for item in items],))
                if cursor.fetchone()[0] != expected:
                    raise ValueError('Contagem de fontes divergiu')
        return expected

    @task
    def confirmar(expected):
        import os
        import psycopg2
        with psycopg2.connect(os.environ['DATAMIND_DB_DSN']) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT current_database(), count(*) FROM audit.source_file')
                database,count=cursor.fetchone()
                if count != expected: raise ValueError('Numero inesperado de fontes')
        print(f'Banco {database}: {count} fontes verificadas. Ambiente pronto para implementar ETL.')

    confirmar(registrar_manifesto(validar_fontes()))

environment_dag()
