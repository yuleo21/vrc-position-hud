#Requires -Version 7

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$unityPackage = Get-ChildItem -Path $root -Filter "PositionHUD_v*.unitypackage" | Select-Object -First 1
if (-not $unityPackage) {
    throw "PositionHUD_v*.unitypackage not found in $root"
}
if ($unityPackage.BaseName -notmatch '^PositionHUD_v[\d.]+$') {
    throw "unexpected unitypackage name: $($unityPackage.Name)"
}
$releaseName = $unityPackage.BaseName

$distDir = Join-Path $root "dist"
$stagingRoot = Join-Path $distDir "_staging"
$stagingDir = Join-Path $stagingRoot $releaseName
$zipPath = Join-Path $distDir "$releaseName.zip"

if (Test-Path $stagingRoot) {
    Remove-Item $stagingRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $stagingDir -Force | Out-Null

Copy-Item -Path (Join-Path $root "LICENSE") -Destination $stagingDir
Copy-Item -Path (Join-Path $root "README.md") -Destination $stagingDir
Copy-Item -Path $unityPackage.FullName -Destination $stagingDir

robocopy (Join-Path $root "decoder") (Join-Path $stagingDir "decoder") /E `
    /XD .venv __pycache__ .pytest_cache .ruff_cache dist build `
    /XF "*.pyc" | Out-Null
if ($LASTEXITCODE -ge 8) {
    throw "robocopy failed with exit code $LASTEXITCODE"
}

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
Compress-Archive -Path $stagingDir -DestinationPath $zipPath -Force

Remove-Item $stagingRoot -Recurse -Force

Write-Host "created: $zipPath"
exit 0
