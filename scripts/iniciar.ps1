. (Join-Path $PSScriptRoot 'language.ps1')
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host (Get-ProjectMessage 'Ambiente ainda não configurado. Executando a configuração...' 'The environment is not set up yet. Running setup...') -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "configurar.ps1")
}

Set-Location -LiteralPath $projectRoot
& $pythonPath -m confereantes.cli
