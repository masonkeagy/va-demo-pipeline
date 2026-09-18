<#
.SYNOPSIS
    Deploys the packaged solution to a target Dataverse environment.

.DESCRIPTION
    Reads environment-specific configuration from /config/{env}.json
    and imports the solution via Power Platform CLI. Applies
    environment variable and connection reference settings post-import.

.EXAMPLE
    ./scripts/deploy.ps1 -Environment dev
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment,

    [string]$PackagePath = "./dist"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Deploy: Environment = $Environment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ------------------------------------------------
# Step 1: Load environment configuration
# ------------------------------------------------
$configPath = "./config/$Environment.json"

if (-not (Test-Path $configPath)) {
    throw "Configuration file not found: $configPath"
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
Write-Host "`n[1/4] Loaded config for '$($config.environment)'" -ForegroundColor Yellow
Write-Host "  Environment URL: $($config.environmentUrl)"
Write-Host "  Solution: $($config.solutionName) v$($config.solutionVersion)"

# ------------------------------------------------
# Step 2: Authenticate to Dataverse
# ------------------------------------------------
Write-Host "`n[2/4] Authenticating to Dataverse..." -ForegroundColor Yellow

$tenantId = [System.Environment]::GetEnvironmentVariable($config.authentication.tenantIdSecretName)
$clientId = [System.Environment]::GetEnvironmentVariable($config.authentication.clientIdSecretName)
$clientSecret = [System.Environment]::GetEnvironmentVariable($config.authentication.clientSecretSecretName)

if (-not $tenantId -or -not $clientId -or -not $clientSecret) {
    Write-Warning "Authentication secrets not found in environment variables."
    Write-Warning "Expected: $($config.authentication.tenantIdSecretName), $($config.authentication.clientIdSecretName), $($config.authentication.clientSecretSecretName)"
    Write-Warning "Skipping live authentication - running in DEMO/MOCK mode."
    $mockMode = $true
} else {
    $mockMode = $false

    pac auth create `
        --tenant $tenantId `
        --applicationId $clientId `
        --clientSecret $clientSecret `
        --url $config.environmentUrl

    if ($LASTEXITCODE -ne 0) {
        throw "Authentication failed with exit code $LASTEXITCODE"
    }
    Write-Host "✓ Authenticated to $($config.environmentUrl)" -ForegroundColor Green
}

# ------------------------------------------------
# Step 3: Import the solution package
# ------------------------------------------------
Write-Host "`n[3/4] Importing solution package..." -ForegroundColor Yellow

$solutionZip = Get-ChildItem -Path $PackagePath -Filter "$($config.solutionName)*.zip" | Select-Object -First 1

if ($mockMode) {
    Write-Host "  [MOCK MODE] Would import solution zip: $($config.solutionName)-*.zip" -ForegroundColor DarkYellow
    Write-Host "  [MOCK MODE] Target environment: $($config.environmentUrl)" -ForegroundColor DarkYellow
    Write-Host "  [MOCK MODE] Publish after import: $($config.deploymentSettings.publishAfterImport)" -ForegroundColor DarkYellow
    Write-Host "  [MOCK MODE] Holding solution: $($config.deploymentSettings.holdingSolution)" -ForegroundColor DarkYellow
    Write-Host "✓ [MOCK MODE] Simulated import complete" -ForegroundColor Green
}
elseif (-not $solutionZip) {
    throw "No solution package found matching '$($config.solutionName)*.zip' in $PackagePath"
}
else {
    pac solution import `
        --path $solutionZip.FullName `
        --publish-changes $config.deploymentSettings.publishAfterImport `
        --force-overwrite $config.deploymentSettings.overwriteUnmanagedCustomizations `
        --skip-dependency-check $config.deploymentSettings.skipProductUpdateDependencies `
        --async

    if ($LASTEXITCODE -ne 0) {
        throw "Solution import failed with exit code $LASTEXITCODE"
    }
    Write-Host "✓ Solution imported: $($solutionZip.Name)" -ForegroundColor Green
}

# ------------------------------------------------
# Step 4: Apply environment variables & connection references
# ------------------------------------------------
Write-Host "`n[4/4] Applying environment variables..." -ForegroundColor Yellow

if ($mockMode) {
    foreach ($key in $config.environmentVariables.PSObject.Properties.Name) {
        $value = $config.environmentVariables.$key
        Write-Host "  [MOCK MODE] Would set '$key' = '$value'" -ForegroundColor DarkYellow
    }
    Write-Host "✓ [MOCK MODE] Simulated environment variable configuration complete" -ForegroundColor Green
} else {
    foreach ($key in $config.environmentVariables.PSObject.Properties.Name) {
        $value = $config.environmentVariables.$key

        pac env variable set `
            --name $key `
            --value $value

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to set environment variable '$key' (continuing)"
        } else {
            Write-Host "  ✓ Set '$key' = '$value'" -ForegroundColor Green
        }
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ Deployment Complete: $Environment" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan