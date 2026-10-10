[CmdletBinding()]
param([switch]$Build)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

function Invoke-Docker {
    param([string[]]$Arguments)
    & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker falhou: $($Arguments -join ' ')" }
}

Get-Command docker -ErrorAction Stop | Out-Null
$dockerOS = & docker info --format '{{.OSType}}'
if ($LASTEXITCODE -ne 0 -or $dockerOS -ne 'linux') {
    throw 'Inicie o Docker Desktop no modo de conteineres Linux.'
}

if (-not (Test-Path -LiteralPath '.env') -or -not (Test-Path -LiteralPath 'runtime/private/passwords.json')) {
    $pythonReady = $false
    $candidates = @(
        @{ Command = 'py'; Prefix = @('-3') },
        @{ Command = 'python'; Prefix = @() },
        @{ Command = (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'); Prefix = @() }
    )
    foreach ($candidate in $candidates) {
        $pythonCommand = Get-Command $candidate.Command -ErrorAction SilentlyContinue
        if (-not $pythonCommand) { continue }
        $pythonArgs = @($candidate.Prefix) + @('-c', 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)')
        & $pythonCommand.Source @pythonArgs 2>$null
        if ($LASTEXITCODE -ne 0) { continue }
        $setupArgs = @($candidate.Prefix) + @('src/setup_local.py')
        & $pythonCommand.Source @setupArgs
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao configurar credenciais locais.' }
        $pythonReady = $true
        break
    }
    if (-not $pythonReady) { throw 'Instale Python 3.11+ e execute novamente.' }
}

foreach ($folder in @('data/raw','runtime/etl','outputs/analytics')) {
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}
Invoke-Docker -Arguments @('compose','config','--quiet')
& docker image inspect datamind03-airflow:3.3.2 --format '{{.Id}}' 2>$null | Out-Null
$imageMissing = $LASTEXITCODE -ne 0
if ($Build -or $imageMissing) { Invoke-Docker -Arguments @('compose','build') }
Invoke-Docker -Arguments @('compose','up','-d','--wait','postgres-meta','postgres-data')
Invoke-Docker -Arguments @('compose','exec','-T','postgres-data','psql','-v','ON_ERROR_STOP=1','-U','datamind','-d','datamind03','-f','/docker-entrypoint-initdb.d/001_schemas.sql')
Invoke-Docker -Arguments @('compose','run','--rm','airflow-init')
Invoke-Docker -Arguments @('compose','up','-d','--wait','airflow-api','airflow-scheduler','airflow-dag-processor')
Write-Output 'Airflow pronto em http://localhost:8080. Credenciais: runtime/private/ACESSO_LOCAL.txt'
