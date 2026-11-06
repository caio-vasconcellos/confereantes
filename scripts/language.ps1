function Get-ProjectMessage([string]$Portuguese, [string]$English) {
    if ($env:CONFEREANTES_LANG -eq 'en') { return $English }
    return $Portuguese
}
