param (
    [Parameter(Mandatory)]
    [ValidateSet('dev', 'prod')]
    [string]$Mode
)

$ProjectRoot = "$PSScriptRoot\.."
Set-Location $ProjectRoot
$env:PYTHONPATH = $ProjectRoot

$VenvScripts = "$ProjectRoot\.venv\Scripts"

if ($Mode -eq 'dev')
{
    $Environment = 'development'
}
else
{
    $Environment = 'production'
    & "$VenvScripts\pip" install -r "$ProjectRoot\requirements.txt"
}

Copy-Item -Path "$ProjectRoot\.env.$Environment" -Destination "$ProjectRoot\.env"

$TranslationDir = "$ProjectRoot\resources\translations"
$Languages = 'en', 'et'
$Domain = 'messages'

foreach ($Lang in $Languages)
{
    msgfmt -o $TranslationDir\$Lang\LC_MESSAGES\$Domain.mo $TranslationDir\$Lang\LC_MESSAGES\$Domain.po
}

& "$VenvScripts\python.exe" -m src.main

