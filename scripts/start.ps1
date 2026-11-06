$previousLanguage = $env:CONFEREANTES_LANG
try {
    $env:CONFEREANTES_LANG = 'en'
    & (Join-Path $PSScriptRoot 'iniciar.ps1')
} finally { $env:CONFEREANTES_LANG = $previousLanguage }
