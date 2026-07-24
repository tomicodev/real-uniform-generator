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
if (-not (Test-Path (Join-Path $AddonDir "blender_manifest.toml"))) {
    throw "blender_manifest.toml was not found in: $AddonDir"
}
if (-not (Test-Path $TestScript)) {
    throw "Smoke test was not found: $TestScript"
}

if (Test-Path $DistDir) {
    Remove-Item $DistDir -Recurse -Force
}
New-Item -ItemType Directory -Path $DistDir | Out-Null

if (-not (Test-Path $BlenderExe)) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $AddonDir,
        $ZipPath,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $false
    )
    Write-Warning "Blender executable was not found: $BlenderExe"
    Write-Warning "A fallback ZIP was created, but Blender validation and the smoke test were skipped."
    Write-Host "Created install ZIP: $ZipPath" -ForegroundColor Yellow
    exit 0
}

Write-Host "Building Blender extension package..." -ForegroundColor Cyan
& $BlenderExe --command extension build --source-dir $AddonDir --output-filepath $ZipPath
if ($LASTEXITCODE -ne 0) {
    throw "Blender extension build failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path $ZipPath)) {
    throw "Blender did not create the extension ZIP: $ZipPath"
}

Write-Host "Validating extension package..." -ForegroundColor Cyan
& $BlenderExe --command extension validate $ZipPath
if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed with exit code $LASTEXITCODE"
}

Write-Host "Running Blender generation and export smoke test..." -ForegroundColor Cyan
& $BlenderExe --background --factory-startup --python $TestScript
if ($LASTEXITCODE -ne 0) {
    throw "Blender smoke test failed with exit code $LASTEXITCODE"
}

Write-Host "RUG_SMOKE_TEST_OK" -ForegroundColor Green
Write-Host "Install this file from Blender: $ZipPath" -ForegroundColor Green
