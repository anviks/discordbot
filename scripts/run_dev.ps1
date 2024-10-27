$ProjectRoot = "$PSScriptRoot\.."
Set-Location $ProjectRoot
$env:PYTHONPATH = $ProjectRoot

$VenvScripts = "$ProjectRoot\.venv\Scripts"

Copy-Item -Path "$ProjectRoot\.env.development" -Destination "$ProjectRoot\.env"

$TranslationDir = "$ProjectRoot\resources\translations"
$Languages = 'en', 'et'
$Domain = 'messages'

foreach ($Lang in $Languages)
{
    msgfmt -o $TranslationDir\$Lang\LC_MESSAGES\$Domain.mo $TranslationDir\$Lang\LC_MESSAGES\$Domain.po
}

& "$VenvScripts\python.exe" -m src.main
