$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& docker compose ps -a
if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar os servicos Docker.' }
$runningServices = @(& docker compose ps --status running --services)
if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar servicos ativos.' }
if ($runningServices -notcontains 'airflow-scheduler') {
    Write-Output 'Airflow parado. Execute scripts/iniciar.ps1 quando desejar iniciar.'
    return
}
& docker compose exec -T airflow-scheduler airflow dags list
if ($LASTEXITCODE -ne 0) { throw 'Falha ao listar DAGs.' }
& docker compose exec -T airflow-scheduler airflow dags list-import-errors
if ($LASTEXITCODE -ne 0) { throw 'Falha ao verificar importacao das DAGs.' }
