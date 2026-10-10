[CmdletBinding()]
param([switch]$NoBrowser)
$ErrorActionPreference='Stop'
$scriptPath=Join-Path $PSScriptRoot 'scripts\iniciar_prototipo.ps1'
if($NoBrowser){& $scriptPath -NoBrowser}else{& $scriptPath}
if($LASTEXITCODE -and $LASTEXITCODE -ne 0){throw 'Falha ao abrir o protótipo.'}