. (Join-Path $PSScriptRoot 'language.ps1')
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$pythonPath = Join-Path $venvPath "Scripts\python.exe"

Set-Location -LiteralPath $projectRoot

if (-not (Test-Path -LiteralPath $pythonPath)) {
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host (Get-ProjectMessage 'O modulo venv nao esta disponivel. Tentando a alternativa virtualenv...' 'The venv module is unavailable. Trying virtualenv...') -ForegroundColor Yellow
        python -m pip install --user virtualenv
        if ($LASTEXITCODE -ne 0) {
            throw (Get-ProjectMessage 'Nao foi possivel instalar o virtualenv.' 'Could not install virtualenv.')
        }
        python -m virtualenv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw (Get-ProjectMessage 'Nao foi possivel criar o ambiente virtual.' 'Could not create the virtual environment.')
        }
    }
}

& $pythonPath -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw (Get-ProjectMessage 'Nao foi possivel atualizar o pip.' 'Could not update pip.') }
& $pythonPath -m pip install -e ".[ocr,dev]"
if ($LASTEXITCODE -ne 0) { throw (Get-ProjectMessage 'Nao foi possivel instalar o ConfereAntes.' 'Could not install ConfereAntes.') }

Write-Host ""
Write-Host (Get-ProjectMessage 'ConfereAntes configurado.' 'ConfereAntes is ready.') -ForegroundColor Green
Write-Host (Get-ProjectMessage 'Use .\scripts\iniciar.ps1 para abrir o aplicativo.' 'Run .\scripts\start.ps1 to open the app.')
