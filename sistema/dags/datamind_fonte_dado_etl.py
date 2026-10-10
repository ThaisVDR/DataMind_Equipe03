"""ETL das 31 fontes locais para PostgreSQL, com publicacao atomica do lote."""
from datetime import datetime,timedelta,timezone
from airflow.sdk import dag,task,get_current_context

def pipeline():
    import sys
    path='/opt/airflow/project/src'
    if path not in sys.path:sys.path.insert(0,path)
    import fonte_dado_etl
    return fonte_dado_etl

@dag(dag_id='datamind_fonte_dado_etl',schedule=None,catchup=False,max_active_runs=1,
     max_active_tasks=2,start_date=datetime(2026,10,10,tzinfo=timezone.utc),
     default_args={'retries':1,'retry_delay':timedelta(seconds=20)},
     tags=['datamind','etl','postgresql','fonteDado'],
     description='31 fontes: trajetorias 2015-2020, Censo 2021-2024, indicadores INEP e IBGE MT.')
def etl():
    @task
    def inventariar():return pipeline().discover(get_current_context()['run_id'])
    @task
    def extrair_transformar_carregar(item):
        from airflow.exceptions import AirflowFailException
        try:return pipeline().process_source(item)
        except (ValueError,KeyError) as exc:raise AirflowFailException(str(exc)) from exc
    @task
    def publicar_lote(results):
        from airflow.exceptions import AirflowFailException
        context=get_current_context()
        try:return pipeline().publish(results,context['run_id'],(context['dag_run'].conf or {}).get('force_validation_failure') is True)
        except ValueError as exc:raise AirflowFailException(str(exc)) from exc
    publicar_lote(extrair_transformar_carregar.expand(item=inventariar()))

etl()
