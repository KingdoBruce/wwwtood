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
$portable = Join-Path $blogRoot 'TOOD-Studio-Windows'
$iconSource = Join-Path $portable 'ico.png'
if (-not (Test-Path -LiteralPath $iconSource)) {
    throw "Icon source not found: $iconSource"
}
$iconTemp = Join-Path $studioRoot 'ico.png'
Copy-Item -LiteralPath $iconSource -Destination $iconTemp -Force
$iconIco = Join-Path $studioRoot 'TOOD-Studio.ico'
& $python -c "import sys; from PIL import Image; image=Image.open(sys.argv[1]).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS); image.save(sys.argv[2],format='ICO',sizes=[(16,16),(20,20),(24,24),(32,32),(40,40),(48,48),(64,64),(128,128),(256,256)])" $iconTemp $iconIco
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $iconIco)) {
    throw "Windows multi-size icon generation failed"
}

Push-Location $studioRoot
try {
    & $python -m PyInstaller --noconfirm --clean --onedir `
        --name 'TOOD-Studio' `
        --windowed `
        --add-data 'templates;templates' `
        --add-data 'static;static' `
        --add-binary 'bin\hugo.exe;bin' `
        --icon 'TOOD-Studio.ico' `
        --collect-all markdown `
        app.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$output = Join-Path $studioRoot 'dist\TOOD-Studio'

if (Test-Path -LiteralPath $portable) {
    Remove-Item -LiteralPath $portable -Recurse -Force
}
Copy-Item -LiteralPath $output -Destination $portable -Recurse -Force
Copy-Item -LiteralPath $iconTemp -Destination (Join-Path $portable 'ico.png') -Force
Remove-Item -LiteralPath $iconTemp -Force
Remove-Item -LiteralPath $iconIco -Force

Write-Output "BUILD_OK=$output"
Write-Output "PORTABLE_APP=$portable"
Write-Output "PORTABLE_EXE=$(Join-Path $portable 'TOOD-Studio.exe')"
