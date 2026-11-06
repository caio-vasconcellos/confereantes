param([switch]$NoBrowser)
$previousLanguage = $env:CONFEREANTES_LANG
$previousDotnetLanguage = $env:DOTNET_CLI_UI_LANGUAGE
try {
    $env:CONFEREANTES_LANG = 'en'
    $env:DOTNET_CLI_UI_LANGUAGE = 'en'
    & (Join-Path $PSScriptRoot 'iniciar-completo.ps1') -SemNavegador:$NoBrowser
} finally {
    $env:CONFEREANTES_LANG = $previousLanguage
    $env:DOTNET_CLI_UI_LANGUAGE = $previousDotnetLanguage
}
