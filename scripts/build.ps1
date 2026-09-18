<#
.SYNOPSIS
    Builds the D365 Customer Service demo solution components.

.DESCRIPTION
    Compiles the .NET plugin assembly and bundles the WebResources/PCF
    control for packaging. Mirrors the intent of Stage 2/4 in the
    GitHub Actions pipeline but runnable locally for development.

.EXAMPLE
    ./scripts/build.ps1 -Configuration Release
#>

param(
    [string]$Configuration = "Debug",
    [string]$SolutionName = "CustomerServiceDemo"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Build: $SolutionName ($Configuration)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ------------------------------------------------
# Step 1: Build .NET Plugin Assembly
# ------------------------------------------------
Write-Host "`n[1/3] Building Plugin assembly (.NET)..." -ForegroundColor Yellow

$pluginProjectPath = "./src/Plugins"

if (Test-Path $pluginProjectPath) {
    dotnet build $pluginProjectPath --configuration $Configuration
    if ($LASTEXITCODE -ne 0) {
        throw "Plugin build failed with exit code $LASTEXITCODE"
    }
    Write-Host "✓ Plugin assembly built successfully" -ForegroundColor Green
} else {
    Write-Warning "Plugin project path not found: $pluginProjectPath (skipping)"
}

# ------------------------------------------------
# Step 2: Build/Bundle PCF Control
# ------------------------------------------------
Write-Host "`n[2/3] Building PCF control (TypeScript)..." -ForegroundColor Yellow

$pcfProjectPath = "./src/PCF/CustomerPriorityControl"

if (Test-Path $pcfProjectPath) {
    Push-Location $pcfProjectPath
    try {
        if (Test-Path "package.json") {
            npm install --silent
            npm run build
            if ($LASTEXITCODE -ne 0) {
                throw "PCF build failed with exit code $LASTEXITCODE"
            }
            Write-Host "✓ PCF control built successfully" -ForegroundColor Green
        } else {
            Write-Warning "No package.json found in PCF folder (skipping)"
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Warning "PCF project path not found: $pcfProjectPath (skipping)"
}

# ------------------------------------------------
# Step 3: Validate WebResources (lint/syntax check)
# ------------------------------------------------
Write-Host "`n[3/3] Validating WebResources (JavaScript)..." -ForegroundColor Yellow

$webResourcesPath = "./src/WebResources"

if (Test-Path $webResourcesPath) {
    Get-ChildItem -Path $webResourcesPath -Filter "*.js" | ForEach-Object {
        node --check $_.FullName
        if ($LASTEXITCODE -ne 0) {
            throw "Syntax error in WebResource: $($_.Name)"
        }
        Write-Host "  ✓ $($_.Name) - syntax OK" -ForegroundColor Green
    }
} else {
    Write-Warning "WebResources path not found: $webResourcesPath (skipping)"
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ Build Complete" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan