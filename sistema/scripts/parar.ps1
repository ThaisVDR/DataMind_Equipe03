$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& docker compose stop
if ($LASTEXITCODE -ne 0) { throw 'Falha ao parar os servicos.' }
Write-Output 'Servicos parados. Volumes dos bancos e logs preservados.'
