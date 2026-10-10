"""Verifica API autenticada e resultados das duas execucoes, sem imprimir segredos."""
import json
import subprocess
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

def command(*args):
    return subprocess.check_output(['docker','compose',*args],text=True,encoding='utf-8').strip()

root=Path(__file__).resolve().parents[1]
password=json.loads((root/'runtime/private/passwords.json').read_text())['datamind03']
request=urllib.request.Request('http://localhost:8080/auth/token',
    data=json.dumps({'username':'datamind03','password':password}).encode(),
    headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request,timeout=15) as response:
    token=json.load(response)['access_token']

def api(path):
    request=urllib.request.Request('http://localhost:8080/api/v2/'+path,
                                  headers={'Authorization':'Bearer '+token})
    with urllib.request.urlopen(request,timeout=15) as response:return json.load(response)

dag=api('dags/datamind_validar_ambiente')
runs=api('dags/datamind_validar_ambiente/dagRuns')['dag_runs']
verified=[r for r in runs if r['dag_run_id'] in ('validacao_01','validacao_02')]
assert len(verified)==2 and all(r['state']=='success' for r in verified), 'Duas execucoes ainda nao concluiram'
db_count=int(command('exec','-T','postgres-data','psql','-U','datamind','-d','datamind03','-Atc',
                     'SELECT count(*) FROM audit.source_file'))
assert db_count==5
services=command('ps','--format','{{.Service}} {{.State}} {{.Health}}').splitlines()
assert len(services)==5 and all('running healthy' in s for s in services)
out={
    'checked_at_utc':datetime.now(timezone.utc).isoformat(),
    'login_verified':True,'dag':dag['dag_id'],'services':services,
    'runs':[{'id':r['dag_run_id'],'state':r['state'],'start':r['start_date'],'end':r['end_date']} for r in verified],
    'registered_sources':db_count,
    'postgres_version':command('exec','-T','postgres-data','psql','-U','datamind','-d','datamind03','-Atc','SHOW server_version'),
    'scope':'Manifesto e conectividade; nao e validacao de idempotencia do ETL analitico completo.'
}
folder=root/'outputs/ambiente';folder.mkdir(parents=True,exist_ok=True)
(folder/'validacao.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
