param(
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$AddonDir = Join-Path $RepoRoot "real_uniform_generator"
$TestScript = Join-Path $RepoRoot "tests\blender_smoke_test.py"
$DistDir = Join-Path $RepoRoot "dist"
$ZipPath = Join-Path $DistDir "real_uniform_generator-v0.2.0.zip"

if (-not (Test-Path $AddonDir)) {
    throw "Add-on folder was not found: $AddonDir"
}

if (Test-Path $DistDir) {
    Remove-Item $DistDir -Recurse -Force
}
New-Item -ItemType Directory -Path $DistDir | Out-Null

Compress-Archive -Path $AddonDir -DestinationPath $ZipPath -CompressionLevel Optimal
Write-Host "Created install ZIP: $ZipPath" -ForegroundColor Green

if (-not (Test-Path $BlenderExe)) {
    Write-Warning "Blender executable was not found: $BlenderExe"
    Write-Warning "The ZIP was created, but the Blender smoke test was skipped."
    exit 0
}

Write-Host "Running Blender smoke test..." -ForegroundColor Cyan
& $BlenderExe --background --factory-startup --python $TestScript
if ($LASTEXITCODE -ne 0) {
    throw "Blender smoke test failed with exit code $LASTEXITCODE"
}

Write-Host "Blender smoke test passed." -ForegroundColor Green
Write-Host "Install this file from Blender: $ZipPath" -ForegroundColor Green
