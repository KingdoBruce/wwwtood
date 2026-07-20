$ErrorActionPreference = 'Stop'
$studioRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$blogRoot = Split-Path -Parent $studioRoot
$venv = Join-Path $studioRoot '.venv'

if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) {
    python -m venv $venv
}

$python = Join-Path $venv 'Scripts\python.exe'
& $python -m pip install -r (Join-Path $studioRoot 'requirements.txt')

$hugo = (Get-Command hugo -ErrorAction Stop).Source
$binDir = Join-Path $studioRoot 'bin'
New-Item -ItemType Directory -Force -Path $binDir | Out-Null
Copy-Item -LiteralPath $hugo -Destination (Join-Path $binDir 'hugo.exe') -Force

Push-Location $studioRoot
try {
    & $python -m PyInstaller --noconfirm --clean --onedir `
        --name 'TOOD-Studio' `
        --add-data 'templates;templates' `
        --add-data 'static;static' `
        --add-binary 'bin\hugo.exe;bin' `
        --collect-all markdown `
        app.py
}
finally {
    Pop-Location
}

$output = Join-Path $studioRoot 'dist\TOOD-Studio'
$portable = Join-Path $blogRoot 'TOOD-Studio-Windows'
$archive = Join-Path $blogRoot 'TOOD-Studio-Windows.zip'

if (Test-Path -LiteralPath $portable) {
    Remove-Item -LiteralPath $portable -Recurse -Force
}
Copy-Item -LiteralPath $output -Destination $portable -Recurse -Force

if (Test-Path -LiteralPath $archive) {
    Remove-Item -LiteralPath $archive -Force
}
Compress-Archive -Path (Join-Path $portable '*') -DestinationPath $archive -CompressionLevel Optimal

Write-Output "BUILD_OK=$output"
Write-Output "PORTABLE_APP=$portable"
Write-Output "PORTABLE_EXE=$(Join-Path $portable 'TOOD-Studio.exe')"
Write-Output "PORTABLE_ZIP=$archive"
