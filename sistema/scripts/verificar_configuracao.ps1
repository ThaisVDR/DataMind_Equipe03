$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
foreach ($path in @('../Fonte de Dados','dags','src','sql/init','data/raw','outputs/fase1','outputs/analytics','runtime/etl','runtime/private')) {
    if (-not (Test-Path -LiteralPath $path -PathType Container)) { throw "Pasta ausente: $path" }
}
foreach ($path in @('.env','runtime/private/passwords.json','outputs/fase1/manifesto.json')) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Arquivo local ausente: $path" }
}
& docker compose config --quiet
if ($LASTEXITCODE -ne 0) { throw 'Configuracao Compose invalida.' }
Write-Output 'Configuracao e caminhos conferidos. Nenhum servico foi iniciado.'
