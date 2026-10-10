param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$dashboard = Join-Path $PSScriptRoot '..\dashboard'
$dashboard = (Resolve-Path -LiteralPath $dashboard).Path
if (-not (Test-Path -LiteralPath (Join-Path $dashboard 'data.js'))) {
    throw 'dashboard/data.js não encontrado. Execute primeiro .\scripts\atualizar_prototipo.ps1.'
}
$url = 'http://127.0.0.1:4173/'
try {
    Invoke-WebRequest -Uri $url -TimeoutSec 2 | Out-Null
} catch {
    $python = Get-Command python -ErrorAction SilentlyContinue
    $prefix = @()
    if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue; $prefix = @('-3') }
    if (-not $python) { throw 'Instale Python 3.11+ para abrir o protótipo local.' }
    $args = $prefix + @('-m','http.server','4173','--bind','127.0.0.1','--directory',$dashboard)
    $proc = Start-Process -FilePath $python.Source -ArgumentList $args -WorkingDirectory $dashboard -WindowStyle Hidden -PassThru
    $pidPath = Join-Path $PSScriptRoot 'runtime/prototipo_server.pid'
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $pidPath) | Out-Null
    Set-Content -LiteralPath $pidPath -Value $proc.Id -Encoding ascii
    $ready = $false
    for ($i=0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 250
        try { Invoke-WebRequest -Uri $url -TimeoutSec 1 | Out-Null; $ready = $true; break } catch { }
    }
    if (-not $ready) { throw 'O servidor local não iniciou. Confira se a porta 4173 está livre.' }
}
if (-not $NoBrowser) { Start-Process $url }
Write-Output "Protótipo aberto em $url"
