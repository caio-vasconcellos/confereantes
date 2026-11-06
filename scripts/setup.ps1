$previousLanguage = $env:CONFEREANTES_LANG
try {
    $env:CONFEREANTES_LANG = 'en'
    & (Join-Path $PSScriptRoot 'configurar.ps1')
} finally { $env:CONFEREANTES_LANG = $previousLanguage }
