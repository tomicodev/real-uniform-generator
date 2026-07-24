param(
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$AddonDir = Join-Path $RepoRoot "real_uniform_generator"
$SourceTestScript = Join-Path $RepoRoot "tests\blender_smoke_test.py"
$InstalledTestScript = Join-Path $RepoRoot "tests\installed_extension_smoke_test.py"
$DistDir = Join-Path $RepoRoot "dist"
$ZipPath = Join-Path $DistDir "real_uniform_generator-v0.2.0.zip"

if (-not (Test-Path $AddonDir)) {
    throw "Add-on folder was not found: $AddonDir"
}
if (-not (Test-Path (Join-Path $AddonDir "blender_manifest.toml"))) {
    throw "blender_manifest.toml was not found in: $AddonDir"
}
foreach ($TestScript in @($SourceTestScript, $InstalledTestScript)) {
    if (-not (Test-Path $TestScript)) {
        throw "Smoke test was not found: $TestScript"
    }
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
    Write-Warning "A fallback ZIP was created, but Blender validation and smoke tests were skipped."
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

Write-Host "Running source-tree generation and export smoke test..." -ForegroundColor Cyan
& $BlenderExe --background --factory-startup --python-exit-code 1 --python $SourceTestScript
if ($LASTEXITCODE -ne 0) {
    throw "Source-tree smoke test failed with exit code $LASTEXITCODE"
}

$PreviousUserResources = $env:BLENDER_USER_RESOURCES
$TestUserResources = Join-Path ([System.IO.Path]::GetTempPath()) ("rug_blender_user_" + [Guid]::NewGuid().ToString("N"))
$TestRepositoryDirectory = Join-Path $TestUserResources "extension_repository"
New-Item -ItemType Directory -Path $TestRepositoryDirectory -Force | Out-Null

try {
    $env:BLENDER_USER_RESOURCES = $TestUserResources

    Write-Host "Creating isolated Blender extension repository..." -ForegroundColor Cyan
    & $BlenderExe --command extension repo-add `
        --name "RUG Test" `
        --directory $TestRepositoryDirectory `
        --source USER `
        --clear-all `
        rug_test
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the isolated extension repository: $LASTEXITCODE"
    }

    Write-Host "Installing and enabling packaged extension..." -ForegroundColor Cyan
    & $BlenderExe --command extension install-file -r rug_test -e $ZipPath
    if ($LASTEXITCODE -ne 0) {
        throw "Packaged extension installation failed with exit code $LASTEXITCODE"
    }

    Write-Host "Running installed-extension end-to-end test..." -ForegroundColor Cyan
    & $BlenderExe --background --python-exit-code 1 --python $InstalledTestScript
    if ($LASTEXITCODE -ne 0) {
        throw "Installed-extension smoke test failed with exit code $LASTEXITCODE"
    }
}
finally {
    if ([string]::IsNullOrEmpty($PreviousUserResources)) {
        Remove-Item Env:BLENDER_USER_RESOURCES -ErrorAction SilentlyContinue
    }
    else {
        $env:BLENDER_USER_RESOURCES = $PreviousUserResources
    }
    if (Test-Path $TestUserResources) {
        Remove-Item $TestUserResources -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "RUG_SMOKE_TEST_OK" -ForegroundColor Green
Write-Host "RUG_INSTALLED_EXTENSION_TEST_OK" -ForegroundColor Green
Write-Host "Install this file from Blender: $ZipPath" -ForegroundColor Green
