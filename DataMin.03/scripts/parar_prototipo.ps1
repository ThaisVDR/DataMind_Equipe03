$ErrorActionPreference = 'Stop'
$pidPath = Join-Path $PSScriptRoot 'runtime/prototipo_server.pid'
if (-not (Test-Path -LiteralPath $pidPath)) { Write-Output 'Nenhum servidor iniciado por este projeto.'; exit 0 }
$serverProcessId = [int](Get-Content -LiteralPath $pidPath -Raw)
$proc = Get-Process -Id $serverProcessId -ErrorAction SilentlyContinue
if ($proc -and $proc.ProcessName -in @('python','py')) { Stop-Process -Id $serverProcessId }
Remove-Item -LiteralPath $pidPath -Force
Write-Output 'Servidor local do protótipo encerrado.'
