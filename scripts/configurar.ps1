$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$pythonPath = Join-Path $venvPath "Scripts\python.exe"

Set-Location -LiteralPath $projectRoot

if (-not (Test-Path -LiteralPath $pythonPath)) {
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "O modulo venv nao esta disponivel. Tentando a alternativa virtualenv..." -ForegroundColor Yellow
        python -m pip install --user virtualenv
        if ($LASTEXITCODE -ne 0) {
            throw "Nao foi possivel instalar o virtualenv."
        }
        python -m virtualenv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Nao foi possivel criar o ambiente virtual."
        }
    }
}

& $pythonPath -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel atualizar o pip." }
& $pythonPath -m pip install -e ".[ocr,dev]"
if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel instalar o ConfereAntes." }

Write-Host ""
Write-Host "ConfereAntes configurado." -ForegroundColor Green
Write-Host "Use .\scripts\iniciar.ps1 para abrir o aplicativo."
