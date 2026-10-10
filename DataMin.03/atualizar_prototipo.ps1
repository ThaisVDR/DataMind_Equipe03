$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'scripts\atualizar_prototipo.ps1')
if($LASTEXITCODE -and $LASTEXITCODE -ne 0){throw 'Falha ao atualizar o snapshot.'}