"""Teste de integracao real: carga, repeticao e bloqueio da publicacao.

Executar na raiz do projeto, com Docker e API do Airflow disponiveis.
Nao imprime credenciais. Mantem as evidencias e execucoes para auditoria.
"""
import argparse
import hashlib
import json
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAG = 'datamind_trajetoria_2015'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-run-id', default='trajetoria_validacao_01')
    parser.add_argument('--start-first', action='store_true', help='Inicia a primeira carga; use identificador novo')
    args = parser.parse_args()
    password = json.loads((ROOT/'runtime/private/passwords.json').read_text())['datamind']
    request = urllib.request.Request('http://localhost:8080/auth/token',
        data=json.dumps({'username':'datamind','password':password}).encode(),
        headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request, timeout=15) as response:
        token = json.load(response)['access_token']

    def api(path, data=None):
        request = urllib.request.Request('http://localhost:8080/api/v2/'+path,
            data=None if data is None else json.dumps(data).encode(),
            headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)

    def wait(run_id):
        previous = None
        for _ in range(300):
            run = api(f'dags/{DAG}/dagRuns/{run_id}')
            if run['state'] != previous:
                print(run_id, run['state'], flush=True)
                previous = run['state']
            if run['state'] in ('success','failed'):
                assert run['state']=='success', f'Falha em {run_id}; consultar logs da tarefa'
                return {'run_id':run_id,'state':run['state'],'end':run['end_date']}
            time.sleep(2)
        raise TimeoutError(run_id)

    def snapshot():
        sql = """SELECT json_build_object(
          'core_rows',(SELECT count(*) FROM core.trajectory_active),
          'core_versions',(SELECT count(DISTINCT version) FROM core.trajectory),
          'mart_rows',(SELECT count(*) FROM mart.p1_trajectory_active),
          'publication',(SELECT row_to_json(p) FROM audit.publication p WHERE product='p1_trajetoria_2015'),
          'runs',(SELECT json_agg(r ORDER BY airflow_run_id) FROM audit.trajectory_run r));"""
        out = subprocess.check_output(['docker','compose','exec','-T','postgres-data',
            'psql','-U','datamind','-d','datamind','-Atc',sql],cwd=ROOT,text=True,encoding='utf-8')
        result = json.loads(out)
        pointer_bytes = (ROOT/'outputs/analytics/current.json').read_bytes()
        pointer = json.loads(pointer_bytes)
        blob = (ROOT/'outputs/analytics'/pointer['path']).read_bytes()
        result['export_sha256'] = hashlib.sha256(blob).hexdigest()
        result['pointer_sha256'] = hashlib.sha256(pointer_bytes).hexdigest()
        assert result['export_sha256']==pointer['sha256']
        assert result['publication']['version']==pointer['version']
        assert result['core_rows']==5150 and result['mart_rows']==10
        return result

    if args.start_first:
        api(f'dags/{DAG}/dagRuns', {'dag_run_id':args.first_run_id,'logical_date':None,'conf':{}})
    first = wait(args.first_run_id)
    before = snapshot()
    # Identificadores exclusivos permitem repetir o teste sem conflito na API.
    suffix = str(time.time_ns())
    repeat_id = 'trajetoria_repeticao_'+suffix
    api(f'dags/{DAG}/dagRuns',{'dag_run_id':repeat_id,'logical_date':None,'conf':{}})
    repeat = wait(repeat_id)
    after = snapshot()
    assert before['core_versions']==after['core_versions']
    assert before['publication']['version']==after['publication']['version']
    assert before['export_sha256']==after['export_sha256']
    assert before['pointer_sha256']==after['pointer_sha256']
    fail_id = 'trajetoria_quarentena_'+suffix
    api(f'dags/{DAG}/dagRuns',{'dag_run_id':fail_id,'logical_date':None,
                            'conf':{'force_validation_failure':True}})
    rejected = wait(fail_id)
    final = snapshot()
    assert final['publication']==after['publication']
    assert final['pointer_sha256']==after['pointer_sha256']
    assert final['export_sha256']==after['export_sha256']
    run = next(r for r in final['runs'] if r['airflow_run_id']==fail_id)
    assert run['state']=='quarantined' and run['details']['valid'] is False
    tasks = api(f'dags/{DAG}/dagRuns/{fail_id}/taskInstances')['task_instances']
    states = {t['task_id']:t['state'] for t in tasks}
    assert states['publicar']=='skipped' and states['quarentena']=='success'
    result = {'checked_at_utc':datetime.now(timezone.utc).isoformat(),
              'runs':[first,repeat,rejected], 'first':before,'repeat':after,'rejected':final,
              'rejection_task_states':states,
              'checks':{'repeat_without_duplicates':True,'export_reproducible':True,
                        'rejected_publication_preserves_previous':True},
              'scope':'MT presencial, coorte 2015, referencias 2015-2024. Falha de qualidade simulada; nao testa falha de disco ou rede.'}
    output = ROOT/'outputs/ambiente/validacao_trajetoria.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result['checks']),flush=True)
    print(str(output),flush=True)


if __name__=='__main__':
    main()
