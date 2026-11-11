param([switch]$SemNavegador)
. (Join-Path $PSScriptRoot 'language.ps1')
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { & (Join-Path $PSScriptRoot 'configurar.ps1') }
$dotnetPath = Join-Path $projectRoot '.tools\dotnet\dotnet.exe'
if (-not (Test-Path -LiteralPath $dotnetPath)) {
    $installedDotnet = Get-Command dotnet -ErrorAction SilentlyContinue
    if (-not $installedDotnet) { throw (Get-ProjectMessage 'Instale o SDK .NET 10: https://dotnet.microsoft.com/download/dotnet/10.0' 'Install the .NET 10 SDK: https://dotnet.microsoft.com/download/dotnet/10.0') }
    $dotnetPath = $installedDotnet.Source
}
$env:DOTNET_CLI_HOME = Join-Path $projectRoot '.tools\dotnet-home'
$env:NUGET_PACKAGES = Join-Path $projectRoot '.tools\nuget'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
& $dotnetPath build api\ConfereAntes.Api --nologo
if ($LASTEXITCODE -ne 0) { throw (Get-ProjectMessage 'Falha ao compilar a API C#.' 'Could not build the C# API.') }
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
        if ($apiProcess.HasExited) { throw (Get-ProjectMessage 'A API C# encerrou durante a inicializacao.' 'The C# API stopped during startup.') }
        try {
            $health = Invoke-RestMethod 'http://127.0.0.1:5080/saude' -TimeoutSec 1
            if ($health.status -eq 'ok') { $apiReady = $true; break }
        } catch { Start-Sleep -Milliseconds 300 }
    }
    if (-not $apiReady) { throw (Get-ProjectMessage 'A API C# nao iniciou na porta 5080.' 'The C# API did not start on port 5080.') }
    Write-Host (Get-ProjectMessage 'Modo C# opcional: interface Python + API C# / EF Core. Encerre com Ctrl+C.' 'Optional C# mode: Python interface + C# API / EF Core. Press Ctrl+C to stop.') -ForegroundColor Green
    if ($SemNavegador) { & $pythonPath -m confereantes.cli --no-browser }
    else { & $pythonPath -m confereantes.cli }
} finally {
    if ($apiProcess -and -not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id }
    $env:CONFEREANTES_SERVICE_TOKEN = $previousToken
    $env:CONFEREANTES_USE_API = $previousApiMode
}
