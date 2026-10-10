[CmdletBinding()]
param([switch]$Build)
$ErrorActionPreference='Stop'
$scriptPath=Join-Path $PSScriptRoot 'scripts\iniciar.ps1'
if($Build){& $scriptPath -Build}else{& $scriptPath}
if($LASTEXITCODE -and $LASTEXITCODE -ne 0){throw 'Falha ao iniciar Airflow.'}