$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'scripts\parar.ps1')
if($LASTEXITCODE -and $LASTEXITCODE -ne 0){throw 'Falha ao parar Airflow.'}