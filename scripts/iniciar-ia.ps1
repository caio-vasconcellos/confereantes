. (Join-Path $PSScriptRoot 'language.ps1')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$ollamaPath = Join-Path $projectRoot '.tools\ollama\ollama.exe'
if (-not (Test-Path -LiteralPath $ollamaPath)) {
    $ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $ollamaCommand) { throw (Get-ProjectMessage 'Instale o Ollama: https://ollama.com/download/windows' 'Install Ollama: https://ollama.com/download/windows') }
    $ollamaPath = $ollamaCommand.Source
}
# Estas variaveis valem somente para este processo e seus filhos.
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_MODELS = Join-Path $projectRoot '.tools\models'
Write-Host (Get-ProjectMessage 'Ollama local. Em outro terminal, execute ollama pull qwen2.5:1.5b uma vez.' 'Local Ollama. In another terminal, run ollama pull qwen2.5:1.5b once.')
& $ollamaPath serve
