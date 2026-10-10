"""Fluxo da apresentacao: extrair, carregar, transformar, conferir e publicar/quarentenar."""
from datetime import datetime,timedelta,timezone
from airflow.sdk import dag,task,get_current_context

def pipeline():
    import sys
    path='/opt/airflow/project/src'
    if path not in sys.path:sys.path.insert(0,path)
    import trajectory_pipeline
    return trajectory_pipeline

@dag(dag_id='datamind_trajetoria_2015',schedule=None,catchup=False,max_active_runs=1,
     start_date=datetime(2026,10,10,tzinfo=timezone.utc),
     default_args={'retries':1,'retry_delay':timedelta(seconds=15)},
     tags=['datamind','trajetoria','P1'],
     description='MT presencial 2015: COPY staging, janelas SQL, validacao, quarentena e versao publicada.')
def trajectory_dag():
    @task
    def extrair():return pipeline().extract(get_current_context()['run_id'])
    @task
    def carregar(c):pipeline().execute('load',c)
    @task
    def transformar(c):pipeline().execute('transform',c)
    @task
    def conferir(c):
        config=get_current_context()['dag_run'].conf or {}
        return pipeline().execute('validate',c,force_failure=config.get('force_validation_failure') is True)
    @task.branch
    def decidir(checks):return 'publicar' if checks['valid'] else 'quarentena'
    @task
    def publicar(c,checks):return pipeline().execute('publish',c,checks=checks)
    @task
    def quarentena(c,checks):return pipeline().quarantine(c,checks)
    c=extrair();loaded=carregar(c);transformed=transformar(c);checks=conferir(c)
    loaded >> transformed >> checks
    branch=decidir(checks)
    branch >> [publicar(c,checks),quarentena(c,checks)]

trajectory_dag()
