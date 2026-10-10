$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'scripts\parar_prototipo.ps1')
if($LASTEXITCODE -and $LASTEXITCODE -ne 0){throw 'Falha ao fechar o protótipo.'}