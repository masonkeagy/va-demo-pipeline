<#
.SYNOPSIS
    Deploys the packaged solution to a target Dataverse environment.

.DESCRIPTION
    Reads environment-specific configuration from /config/{env}.json
    and imports the solution via Power Platform CLI. Applies configured
    Dataverse environment variables after import.

.EXAMPLE
    ./scripts/deploy.ps1 -Environment uat
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("dev", "test", "uat", "prod")]
    [string]$Environment,

    [string]$PackagePath = "./dist",

    [switch]$AllowMock
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Deploy: Environment = $Environment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ------------------------------------------------
# Step 1: Load configuration and locate the solution package
# ------------------------------------------------
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$configPath = Join-Path $repositoryRoot "config/$Environment.json"

if (-not (Test-Path $configPath)) {
    throw "Configuration file not found: $configPath"
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
Write-Host "`n[1/4] Loaded config for '$($config.environment)'" -ForegroundColor Yellow
Write-Host "  Environment URL: $($config.environmentUrl)"
Write-Host "  Solution: $($config.solutionName) v$($config.solutionVersion)"

$packageDirectory = Resolve-Path $PackagePath -ErrorAction Stop
$solutionZip = Get-ChildItem -Path $packageDirectory -Filter "$($config.solutionName)*.zip" |
    Select-Object -First 1

if (-not $solutionZip) {
    throw "No solution package found matching '$($config.solutionName)*.zip' in $packageDirectory"
}

# ------------------------------------------------
# Step 2: Authenticate to Dataverse
# ------------------------------------------------
Write-Host "`n[2/4] Authenticating to Dataverse..." -ForegroundColor Yellow

$tenantId = [System.Environment]::GetEnvironmentVariable($config.authentication.tenantIdSecretName)
$clientId = [System.Environment]::GetEnvironmentVariable($config.authentication.clientIdSecretName)
$clientSecret = [System.Environment]::GetEnvironmentVariable($config.authentication.clientSecretSecretName)

if (-not $tenantId -or -not $clientId -or -not $clientSecret) {
    if (-not $AllowMock) {
        throw "Missing Dataverse credentials. Set environment variables: $($config.authentication.tenantIdSecretName), $($config.authentication.clientIdSecretName), $($config.authentication.clientSecretSecretName). Use -AllowMock only for an explicit local dry run."
    }

    Write-Warning "Credentials are missing; explicit mock mode is enabled. No live deployment will occur."
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

if ($mockMode) {
    Write-Host "  [MOCK MODE] Would import solution zip: $($solutionZip.Name)" -ForegroundColor DarkYellow
    Write-Host "  [MOCK MODE] Target environment: $($config.environmentUrl)" -ForegroundColor DarkYellow
    Write-Host "  [MOCK MODE] Publish after import: $($config.deploymentSettings.publishAfterImport)" -ForegroundColor DarkYellow
    Write-Host "  [MOCK MODE] Holding solution: $($config.deploymentSettings.holdingSolution)" -ForegroundColor DarkYellow
    Write-Host "✓ [MOCK MODE] Dry run complete; no changes were made" -ForegroundColor Green
}
else {
    $importArguments = @("solution", "import", "--path", $solutionZip.FullName)
    if ($config.deploymentSettings.publishAfterImport) {
        $importArguments += "--publish-changes"
    }
    if ($config.deploymentSettings.overwriteUnmanagedCustomizations) {
        $importArguments += "--force-overwrite"
    }
    if ($config.deploymentSettings.skipProductUpdateDependencies) {
        $importArguments += "--skip-dependency-check"
    }

    pac @importArguments

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
            throw "Failed to set environment variable '$key' (exit code $LASTEXITCODE)"
        } else {
            Write-Host "  ✓ Set '$key' = '$value'" -ForegroundColor Green
        }
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ Deployment Complete: $Environment" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan