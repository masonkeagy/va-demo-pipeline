<#
.SYNOPSIS
    Packages the Dataverse solution and build artifacts for deployment.

.DESCRIPTION
    Builds the managed/unmanaged solution zip from the unpacked source
    in /solutions, and stages plugin assemblies + web resources for
    inclusion. Produces a versioned artifact ready for deploy.ps1.

.EXAMPLE
    ./scripts/package.ps1 -SolutionName CustomerServiceDemo -Managed
#>

param(
    [string]$SolutionName = "CustomerServiceDemo",
    [string]$OutputDir = "./dist",
    [switch]$Managed
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Packaging: $SolutionName" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$solutionSourcePath = "./solutions/$SolutionName/src"
$packageType = if ($Managed) { "Managed" } else { "Unmanaged" }
$outputZip = Join-Path $OutputDir "$SolutionName-$packageType.zip"

# ------------------------------------------------
# Step 1: Pack the Dataverse solution
# ------------------------------------------------
Write-Host "`n[1/2] Packing Dataverse solution ($packageType)..." -ForegroundColor Yellow

if (Test-Path $solutionSourcePath) {
    # Requires Power Platform CLI (pac) - https://aka.ms/PowerAppsCLI
    pac solution pack `
        --zipfile $outputZip `
        --folder $solutionSourcePath `
        --packagetype $packageType

    if ($LASTEXITCODE -ne 0) {
        throw "Solution packing failed with exit code $LASTEXITCODE"
    }
    Write-Host "✓ Solution packed: $outputZip" -ForegroundColor Green
} else {
    Write-Warning "Solution source path not found: $solutionSourcePath"
    Write-Warning "Creating placeholder package for demo purposes..."

    # Placeholder so downstream deploy.ps1 has something to reference
    Set-Content -Path $outputZip.Replace(".zip", ".placeholder.txt") `
        -Value "Placeholder for $SolutionName ($packageType) - no live Dataverse connection configured."
}

# ------------------------------------------------
# Step 2: Stage additional build artifacts
# ------------------------------------------------
Write-Host "`n[2/2] Staging build artifacts..." -ForegroundColor Yellow

$artifactPaths = @(
    "./src/Plugins/*/bin/$Configuration",
    "./src/PCF/CustomerPriorityControl/out"
)

foreach ($path in $artifactPaths) {
    if (Test-Path $path) {
        $destName = Split-Path $path -Leaf
        Copy-Item -Path $path -Destination (Join-Path $OutputDir $destName) -Recurse -Force
        Write-Host "  ✓ Staged: $path" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Not found (skipped): $path" -ForegroundColor DarkYellow
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ Packaging Complete" -ForegroundColor Green
Write-Host "Output directory: $OutputDir" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan