$ErrorActionPreference = 'Stop'
$system = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $system
$required = @('postgres-data', 'airflow-scheduler')
$running = @(& docker compose ps --status running --services)
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível consultar o Docker Compose.' }
foreach ($service in $required) {
    if ($running -notcontains $service) {
        throw "O serviço '$service' está parado. Inicie o ambiente com .\scripts\iniciar.ps1 e tente novamente."
    }
}
& docker compose exec -T airflow-scheduler python /opt/airflow/project/src/export_dashboard.py --output /opt/airflow/project/published/prototipo/snapshot.json
if ($LASTEXITCODE -ne 0) { throw 'A exportação do PostgreSQL falhou; o snapshot anterior foi preservado.' }
$snapshotPath = Join-Path $system 'outputs/analytics/prototipo/snapshot.json'
$snapshot = Get-Content -LiteralPath $snapshotPath -Raw
$dataPath = Join-Path $system 'dashboard/data.js'
[System.IO.File]::WriteAllText($dataPath, 'window.DATAMIND = ' + $snapshot + ';', [System.Text.UTF8Encoding]::new($false))
Write-Output "Protótipo atualizado: $dataPath"
