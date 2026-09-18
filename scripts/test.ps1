<#
.SYNOPSIS
    Runs all test suites for the D365 Customer Service demo repo.

.DESCRIPTION
    Executes .NET xUnit tests (Plugins), Jest tests (WebResources),
    and Python pytest tests (tools/data-validation) in sequence.

.EXAMPLE
    ./scripts/test.ps1
#>

param(
    [switch]$SkipDotNet,
    [switch]$SkipJs,
    [switch]$SkipPython
)

$ErrorActionPreference = "Stop"
$failures = @()

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Running Test Suites" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ------------------------------------------------
# .NET Plugin Tests (xUnit)
# ------------------------------------------------
if (-not $SkipDotNet) {
    Write-Host "`n[1/3] Running .NET Plugin tests (xUnit)..." -ForegroundColor Yellow

    $testProjectPath = "./tests/Plugins"

    if (Test-Path $testProjectPath) {
        dotnet test $testProjectPath --logger "trx;LogFileName=plugin-test-results.trx"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ .NET Plugin tests FAILED" -ForegroundColor Red
            $failures += ".NET Plugin Tests"
        } else {
            Write-Host "✓ .NET Plugin tests PASSED" -ForegroundColor Green
        }
    } else {
        Write-Warning "Test project path not found: $testProjectPath (skipping)"
    }
} else {
    Write-Host "`n[1/3] Skipping .NET tests (--SkipDotNet)" -ForegroundColor DarkGray
}

# ------------------------------------------------
# JavaScript WebResource Tests (Jest)
# ------------------------------------------------
if (-not $SkipJs) {
    Write-Host "`n[2/3] Running WebResource tests (Jest)..." -ForegroundColor Yellow

    if (Test-Path "./package.json") {
        npm test -- --ci --reporters=default --reporters=jest-junit
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Jest tests FAILED" -ForegroundColor Red
            $failures += "JavaScript WebResource Tests"
        } else {
            Write-Host "✓ Jest tests PASSED" -ForegroundColor Green
        }
    } else {
        Write-Warning "No root package.json found (skipping Jest tests)"
    }
} else {
    Write-Host "`n[2/3] Skipping JS tests (--SkipJs)" -ForegroundColor DarkGray
}

# ------------------------------------------------
# Python Tests (tools/data-validation)
# ------------------------------------------------
if (-not $SkipPython) {
    Write-Host "`n[3/3] Running Python tests (pytest)..." -ForegroundColor Yellow

    $pythonTestPath = "./tools/data-validation"

    if (Test-Path $pythonTestPath) {
        Push-Location $pythonTestPath
        try {
            pytest tests/ -v --tb=short --cov=read_data --cov-report=term-missing
            if ($LASTEXITCODE -ne 0) {
                Write-Host "✗ Python tests FAILED" -ForegroundColor Red
                $failures += "Python Data Validation Tests"
            } else {
                Write-Host "✓ Python tests PASSED" -ForegroundColor Green
            }
        } finally {
            Pop-Location
        }
    } else {
        Write-Warning "Python test path not found: $pythonTestPath (skipping)"
    }
} else {
    Write-Host "`n[3/3] Skipping Python tests (--SkipPython)" -ForegroundColor DarkGray
}

# ------------------------------------------------
# Summary
# ------------------------------------------------
Write-Host "`n============================================" -ForegroundColor Cyan
if ($failures.Count -eq 0) {
    Write-Host "✓ ALL TEST SUITES PASSED" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "✗ TEST FAILURES DETECTED:" -ForegroundColor Red
    foreach ($f in $failures) {
        Write-Host "  • $f" -ForegroundColor Red
    }
    Write-Host "============================================" -ForegroundColor Cyan
    exit 1
}