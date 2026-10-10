"""Integração real do ETL fonteDado: carga, idempotência e falha de publicação."""
import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
DAG='datamind_fonte_dado_etl'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-run-id',default='fonte_dado_carga_01')
    parser.add_argument('--start-first',action='store_true')
    args=parser.parse_args()
    password=json.loads((ROOT/'runtime/private/passwords.json').read_text())['datamind']
    req=urllib.request.Request('http://localhost:8080/auth/token',data=json.dumps({'username':'datamind','password':password}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as response:token=json.load(response)['access_token']
    def api(path,data=None):
        req=urllib.request.Request('http://localhost:8080/api/v2/'+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
        with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
    def wait(run_id,expected='success'):
        previous=None
        for _ in range(720):
            run=api(f'dags/{DAG}/dagRuns/{run_id}')
            tasks=api(f'dags/{DAG}/dagRuns/{run_id}/taskInstances?limit=100')['task_instances']
            states={}
            for task in tasks:states[task['state'] or 'pending']=states.get(task['state'] or 'pending',0)+1
            progress=json.dumps(states,sort_keys=True)
            if progress!=previous:print(run_id,run['state'],progress,flush=True);previous=progress
            if run['state'] in ('success','failed'):
                assert run['state']==expected, f'Estado inesperado em {run_id}; consultar logs e audit.fd_dataset'
                return {'id':run_id,'state':run['state'],'end':run['end_date']}
            time.sleep(5)
        raise TimeoutError(run_id)
    def query(statement):
        return subprocess.check_output(['docker','compose','exec','-T','postgres-data','psql','-U','datamind','-d','datamind','-Atc',statement],cwd=ROOT,text=True,encoding='utf-8').strip()
    def snapshot():
        result={}
        result['active']=json.loads(query('SELECT json_agg(a ORDER BY source_key) FROM audit.fd_active a'))
        result['sources']=json.loads(query('SELECT json_agg(d ORDER BY source_key) FROM audit.fd_cobertura d'))
        result['tables']={}
        for table in ['fd_trajetoria','fd_censo','fd_indicador','fd_ibge']:
            result['tables'][table]=json.loads(query(f"SELECT json_build_object('rows',count(*),'versions',count(DISTINCT version),'fingerprint',sum(hashtextextended(row_to_json(t)::text,0)::numeric)::text) FROM core.{table} t"))
        result['ibge_special']=json.loads(query("SELECT json_object_agg(status_valor,n) FROM (SELECT status_valor,count(*) n FROM core.ibge_mt GROUP BY status_valor) s"))
        assert int(query("SELECT count(*) FROM core.ibge_mt WHERE (status_valor='zero_absoluto' AND valor IS DISTINCT FROM 0) OR (status_valor IN ('nao_disponivel','nao_aplicavel','inibido') AND valor IS NOT NULL)"))==0
        assert len(result['active'])==31
        return result
    def trigger(run_id,conf):api(f'dags/{DAG}/dagRuns',{'dag_run_id':run_id,'logical_date':None,'conf':conf})
    if args.start_first:trigger(args.first_run_id,{})
    first=wait(args.first_run_id)
    before=snapshot()
    suffix=str(time.time_ns())
    repeat_id='fonte_dado_repeticao_'+suffix
    trigger(repeat_id,{})
    repeat=wait(repeat_id)
    after=snapshot()
    assert before['tables']==after['tables'],'Reexecucao alterou dados ou duplicou registros'
    assert [(r['source_key'],r['version']) for r in before['active']]==[(r['source_key'],r['version']) for r in after['active']]
    rejected_id='fonte_dado_reprovacao_'+suffix
    trigger(rejected_id,{'force_validation_failure':True})
    rejected=wait(rejected_id,'failed')
    final=snapshot()
    assert final['active']==after['active'],'Publicacao alterada por lote reprovado'
    assert final['tables']==after['tables']
    output={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'runs':[first,repeat,rejected],
            'before':before,'repeat':after,'rejected':final,
            'checks':{'idempotency':True,'same_content_fingerprints':True,'rejected_batch_preserves_publication':True,'ibge_zero_distinct_from_missing':True}}
    path=ROOT/'outputs/ambiente/validacao_fonte_dado.json'
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(output['checks']),flush=True)
    print(str(path),flush=True)

if __name__=='__main__':main()
