param([switch]$SemNavegador)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { & (Join-Path $PSScriptRoot 'configurar.ps1') }
$dotnetPath = Join-Path $projectRoot '.tools\dotnet\dotnet.exe'
if (-not (Test-Path -LiteralPath $dotnetPath)) {
    $installedDotnet = Get-Command dotnet -ErrorAction SilentlyContinue
    if (-not $installedDotnet) { throw 'Instale o SDK .NET 10: https://dotnet.microsoft.com/download/dotnet/10.0' }
    $dotnetPath = $installedDotnet.Source
}
$env:DOTNET_CLI_HOME = Join-Path $projectRoot '.tools\dotnet-home'
$env:NUGET_PACKAGES = Join-Path $projectRoot '.tools\nuget'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
& $dotnetPath build api\ConfereAntes.Api --nologo
if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar a API C#.' }
$previousToken = $env:CONFEREANTES_SERVICE_TOKEN
$previousApiMode = $env:CONFEREANTES_USE_API
$apiProcess = $null
try {
    $env:CONFEREANTES_SERVICE_TOKEN = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $env:CONFEREANTES_USE_API = '1'
    $apiDll = Join-Path $projectRoot 'api\ConfereAntes.Api\bin\Debug\net10.0\ConfereAntes.Api.dll'
    $apiProcess = Start-Process -FilePath $dotnetPath -ArgumentList @("`"$apiDll`"") -PassThru -WindowStyle Hidden
    $apiReady = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ($apiProcess.HasExited) { throw 'A API C# encerrou durante a inicializacao.' }
        try {
            $health = Invoke-RestMethod 'http://127.0.0.1:5080/saude' -TimeoutSec 1
            if ($health.status -eq 'ok') { $apiReady = $true; break }
        } catch { Start-Sleep -Milliseconds 300 }
    }
    if (-not $apiReady) { throw 'A API C# nao iniciou na porta 5080.' }
    Write-Host 'Modo completo: Python + C# / EF Core. Encerre com Ctrl+C.' -ForegroundColor Green
    if ($SemNavegador) { & $pythonPath -m confereantes.cli --no-browser }
    else { & $pythonPath -m confereantes.cli }
} finally {
    if ($apiProcess -and -not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id }
    $env:CONFEREANTES_SERVICE_TOKEN = $previousToken
    $env:CONFEREANTES_USE_API = $previousApiMode
}
