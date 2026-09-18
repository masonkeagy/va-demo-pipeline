"""
============================================
D365 Application Compliance & Configuration Validator
============================================
MOCK USE CASE - Replace placeholders with actual schema

This module validates multi-application Excel data against
pipeline compliance requirements (508, SLA, Security, Integration).

PLACEHOLDERS TO REPLACE:
- APP_SHEET_NAMES        -> Your actual sheet/tab names
- COLUMN_* constants      -> Your actual column headers
- File paths              -> Your actual Excel file location
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================
# PLACEHOLDER CONFIGURATION - REPLACE THESE
# ============================================

# TODO: Replace with your actual sheet names in the Excel file
APP_SHEET_NAMES = [
    "AVA Metada (mcs_AVAMetadata)",   # e.g., replace with actual app sheet name
    "APPLICATION_2",
    "CommCare Task (bah_cramtask)",
    "APPLICATION_4",
    "PATS-R Case (mcs_patsrcase)",
    "APPLICATION_6",
    "APPLICATION_7",
    "APPLICATION_8",
]

# TODO: Replace with your actual column names for each validation category
class ColumnNames:
    """Placeholder column name mappings - update to match your Excel headers"""
    
    # Identity / Basic Info columns
    APP_ID = "Application_ID"
    APP_NAME = "Application_Name"
    OWNER = "Business_Owner"
    
    # 508 Compliance columns
    COMPLIANCE_508_STATUS = "508_Compliance_Status"
    COMPLIANCE_508_LAST_AUDIT = "508_Last_Audit_Date"
    COMPLIANCE_508_ISSUES = "508_Open_Issues"
    
    # SLA columns
    SLA_THRESHOLD_HOURS = "SLA_Response_Hours"
    SLA_CURRENT_AVG = "SLA_Current_Avg_Hours"
    SLA_BREACH_COUNT = "SLA_Breach_Count"
    
    # Security / RBAC columns
    SECURITY_LEVEL = "Security_Classification"
    RBAC_ROLES_DEFINED = "RBAC_Roles_Configured"
    FIELD_LEVEL_SECURITY = "Field_Level_Security_Enabled"
    
    # Integration columns
    INTEGRATION_ENDPOINT = "Integration_Endpoint_Name"
    INTEGRATION_STATUS = "Integration_Status"
    INTEGRATION_LAST_TESTED = "Integration_Last_Tested_Date"
    
    # Environment / Deployment columns
    ENVIRONMENT = "Target_Environment"
    DEPLOYMENT_STATUS = "Deployment_Status"


# ============================================
# ENUMS FOR VALIDATION RESULTS
# ============================================

class ComplianceStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_APPLICABLE = "N/A"


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ============================================
# DATA CLASSES FOR VALIDATION RESULTS
# ============================================

@dataclass
class ValidationIssue:
    """Represents a single validation failure or warning"""
    app_name: str
    category: str
    severity: Severity
    message: str
    row_index: Optional[int] = None


@dataclass
class AppValidationResult:
    """Aggregated validation results for a single application"""
    app_name: str
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        if self.total_checks == 0:
            return 0.0
        return round((self.passed_checks / self.total_checks) * 100, 2)
    
    @property
    def status(self) -> ComplianceStatus:
        if self.failed_checks > 0:
            return ComplianceStatus.FAIL
        elif self.warnings > 0:
            return ComplianceStatus.WARNING
        return ComplianceStatus.PASS


# ============================================
# FILE READING FUNCTIONS
# ============================================

def load_application_matrix(filepath: str) -> Dict[str, pd.DataFrame]:
    """
    Load all application sheets from the master Excel file.
    
    Args:
        filepath: Path to the Excel file containing app data
        
    Returns:
        Dictionary mapping sheet_name -> DataFrame
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not Excel format
    """
    if not filepath.endswith(('.xlsx', '.xls')):
        raise ValueError(f"File must be Excel format: {filepath}")
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    all_sheets = pd.read_excel(filepath, sheet_name=None)
    return all_sheets


def filter_known_app_sheets(sheets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Filter the loaded sheets to only include known application sheets.
    Skips any extraneous "notes" or "instructions" tabs.
    
    Args:
        sheets: Dictionary of all sheets loaded from Excel
        
    Returns:
        Filtered dictionary containing only recognized app sheets
    """
    return {
        name: df for name, df in sheets.items()
        if name in APP_SHEET_NAMES
    }


# ============================================
# 508 COMPLIANCE VALIDATION
# ============================================

def validate_508_compliance(df: pd.DataFrame, app_name: str) -> List[ValidationIssue]:
    """
    Validate 508 accessibility compliance status for an application.
    
    Checks:
    - Compliance status is not "FAIL"
    - Last audit date is not stale (placeholder logic)
    - No unresolved open issues
    
    Args:
        df: DataFrame for a single application sheet
        app_name: Name of the application being validated
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    if ColumnNames.COMPLIANCE_508_STATUS not in df.columns:
        issues.append(ValidationIssue(
            app_name=app_name,
            category="508 Compliance",
            severity=Severity.MEDIUM,
            message=f"Missing column: {ColumnNames.COMPLIANCE_508_STATUS}"
        ))
        return issues
    
    for idx, row in df.iterrows():
        status = str(row.get(ColumnNames.COMPLIANCE_508_STATUS, "")).strip().upper()
        
        if status == "FAIL":
            issues.append(ValidationIssue(
                app_name=app_name,
                category="508 Compliance",
                severity=Severity.CRITICAL,
                message=f"508 compliance FAILED for row {idx}",
                row_index=idx
            ))
        elif status not in ("PASS", "FAIL", "N/A", ""):
            issues.append(ValidationIssue(
                app_name=app_name,
                category="508 Compliance",
                severity=Severity.LOW,
                message=f"Unrecognized 508 status value: '{status}' at row {idx}",
                row_index=idx
            ))
        
        # Check for open issues count
        open_issues = row.get(ColumnNames.COMPLIANCE_508_ISSUES, 0)
        if pd.notna(open_issues) and isinstance(open_issues, (int, float)) and open_issues > 0:
            issues.append(ValidationIssue(
                app_name=app_name,
                category="508 Compliance",
                severity=Severity.HIGH,
                message=f"{int(open_issues)} open 508 issue(s) at row {idx}",
                row_index=idx
            ))
    
    return issues


# ============================================
# SLA VALIDATION
# ============================================

def validate_sla_configuration(df: pd.DataFrame, app_name: str) -> List[ValidationIssue]:
    """
    Validate SLA thresholds and breach counts for an application.
    
    Checks:
    - SLA threshold is defined and reasonable
    - Current average doesn't exceed threshold
    - Breach count is not excessive
    
    Args:
        df: DataFrame for a single application sheet
        app_name: Name of the application being validated
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    required_cols = [ColumnNames.SLA_THRESHOLD_HOURS, ColumnNames.SLA_CURRENT_AVG]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        issues.append(ValidationIssue(
            app_name=app_name,
            category="SLA",
            severity=Severity.MEDIUM,
            message=f"Missing SLA columns: {missing_cols}"
        ))
        return issues
    
    for idx, row in df.iterrows():
        threshold = row.get(ColumnNames.SLA_THRESHOLD_HOURS)
        current_avg = row.get(ColumnNames.SLA_CURRENT_AVG)
        breach_count = row.get(ColumnNames.SLA_BREACH_COUNT, 0)
        
        if pd.isna(threshold) or pd.isna(current_avg):
            continue
        
        if current_avg > threshold:
            overage_pct = round(((current_avg - threshold) / threshold) * 100, 1)
            issues.append(ValidationIssue(
                app_name=app_name,
                category="SLA",
                severity=Severity.HIGH,
                message=(
                    f"SLA threshold exceeded at row {idx}: "
                    f"{current_avg}hrs avg vs {threshold}hrs target "
                    f"({overage_pct}% over)"
                ),
                row_index=idx
            ))
        
        if pd.notna(breach_count) and breach_count > 5:  # placeholder threshold
            issues.append(ValidationIssue(
                app_name=app_name,
                category="SLA",
                severity=Severity.MEDIUM,
                message=f"High breach count ({int(breach_count)}) at row {idx}",
                row_index=idx
            ))
    
    return issues


# ============================================
# SECURITY / RBAC VALIDATION
# ============================================

def validate_security_rbac(df: pd.DataFrame, app_name: str) -> List[ValidationIssue]:
    """
    Validate security classification and RBAC configuration.
    
    Checks:
    - Security classification is defined
    - RBAC roles are configured for sensitive apps
    - Field-level security is enabled where required
    
    Args:
        df: DataFrame for a single application sheet
        app_name: Name of the application being validated
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    required_cols = [ColumnNames.SECURITY_LEVEL, ColumnNames.RBAC_ROLES_DEFINED]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        issues.append(ValidationIssue(
            app_name=app_name,
            category="Security/RBAC",
            severity=Severity.MEDIUM,
            message=f"Missing security columns: {missing_cols}"
        ))
        return issues
    
    # Placeholder: define which security levels require extra scrutiny
    HIGH_SENSITIVITY_LEVELS = ["RESTRICTED", "CONFIDENTIAL", "SENSITIVE"]
    
    for idx, row in df.iterrows():
        security_level = str(row.get(ColumnNames.SECURITY_LEVEL, "")).strip().upper()
        rbac_configured = row.get(ColumnNames.RBAC_ROLES_DEFINED, False)
        field_level_security = row.get(ColumnNames.FIELD_LEVEL_SECURITY, False)
        
        if not security_level or security_level == "NAN":
            issues.append(ValidationIssue(
                app_name=app_name,
                category="Security/RBAC",
                severity=Severity.MEDIUM,
                message=f"Security classification not defined at row {idx}",
                row_index=idx
            ))
            continue
        
        # High-sensitivity apps MUST have RBAC configured
        if security_level in HIGH_SENSITIVITY_LEVELS:
            if not rbac_configured or str(rbac_configured).strip().upper() in ("FALSE", "NO", "0", ""):
                issues.append(ValidationIssue(
                    app_name=app_name,
                    category="Security/RBAC",
                    severity=Severity.CRITICAL,
                    message=(
                        f"'{security_level}' classification at row {idx} "
                        f"requires RBAC roles to be configured, but none found"
                    ),
                    row_index=idx
                ))
            
            # High-sensitivity apps should also have field-level security
            if not field_level_security or str(field_level_security).strip().upper() in ("FALSE", "NO", "0", ""):
                issues.append(ValidationIssue(
                    app_name=app_name,
                    category="Security/RBAC",
                    severity=Severity.HIGH,
                    message=(
                        f"'{security_level}' classification at row {idx} "
                        f"should have Field-Level Security enabled"
                    ),
                    row_index=idx
                ))
    
    return issues


# ============================================
# INTEGRATION VALIDATION
# ============================================

def validate_integration_points(df: pd.DataFrame, app_name: str) -> List[ValidationIssue]:
    """
    Validate integration endpoint configuration and testing status.
    
    Checks:
    - Integration endpoints are defined
    - Integration status is not "FAILED" or "DISCONNECTED"
    - Integrations haven't gone untested for too long (placeholder logic)
    
    Args:
        df: DataFrame for a single application sheet
        app_name: Name of the application being validated
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    if ColumnNames.INTEGRATION_STATUS not in df.columns:
        issues.append(ValidationIssue(
            app_name=app_name,
            category="Integration",
            severity=Severity.LOW,
            message=f"Missing column: {ColumnNames.INTEGRATION_STATUS}"
        ))
        return issues
    
    FAILING_STATUSES = ["FAILED", "DISCONNECTED", "ERROR", "OFFLINE"]
    
    for idx, row in df.iterrows():
        status = str(row.get(ColumnNames.INTEGRATION_STATUS, "")).strip().upper()
        endpoint = row.get(ColumnNames.INTEGRATION_ENDPOINT, "Unknown Endpoint")
        last_tested = row.get(ColumnNames.INTEGRATION_LAST_TESTED)
        
        if status in FAILING_STATUSES:
            issues.append(ValidationIssue(
                app_name=app_name,
                category="Integration",
                severity=Severity.CRITICAL,
                message=f"Integration '{endpoint}' status is '{status}' at row {idx}",
                row_index=idx
            ))
        
        # Placeholder: flag if last tested date is missing
        if pd.isna(last_tested):
            issues.append(ValidationIssue(
                app_name=app_name,
                category="Integration",
                severity=Severity.MEDIUM,
                message=f"Integration '{endpoint}' has no last-tested date at row {idx}",
                row_index=idx
            ))
        else:
            # Placeholder: flag if last tested more than 90 days ago
            try:
                last_tested_date = pd.to_datetime(last_tested)
                days_since_test = (pd.Timestamp.now() - last_tested_date).days
                if days_since_test > 90:
                    issues.append(ValidationIssue(
                        app_name=app_name,
                        category="Integration",
                        severity=Severity.MEDIUM,
                        message=(
                            f"Integration '{endpoint}' last tested {days_since_test} "
                            f"days ago (row {idx}) - exceeds 90-day threshold"
                        ),
                        row_index=idx
                    ))
            except (ValueError, TypeError):
                issues.append(ValidationIssue(
                    app_name=app_name,
                    category="Integration",
                    severity=Severity.LOW,
                    message=f"Invalid date format for last-tested at row {idx}",
                    row_index=idx
                ))
    
    return issues


# ============================================
# DEPLOYMENT STATUS VALIDATION
# ============================================

def validate_deployment_status(df: pd.DataFrame, app_name: str) -> List[ValidationIssue]:
    """
    Validate deployment readiness for target environments.
    
    Checks:
    - Deployment status is defined
    - No apps stuck in "FAILED" deployment state
    
    Args:
        df: DataFrame for a single application sheet
        app_name: Name of the application being validated
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    if ColumnNames.DEPLOYMENT_STATUS not in df.columns:
        return issues  # Not critical if missing, skip silently
    
    for idx, row in df.iterrows():
        status = str(row.get(ColumnNames.DEPLOYMENT_STATUS, "")).strip().upper()
        environment = row.get(ColumnNames.ENVIRONMENT, "Unknown Environment")
        
        if status == "FAILED":
            issues.append(ValidationIssue(
                app_name=app_name,
                category="Deployment",
                severity=Severity.HIGH,
                message=f"Deployment to '{environment}' FAILED at row {idx}",
                row_index=idx
            ))
        elif status == "PENDING" and idx == len(df) - 1:  # Placeholder: flag stale pending on last row
            issues.append(ValidationIssue(
                app_name=app_name,
                category="Deployment",
                severity=Severity.LOW,
                message=f"Deployment to '{environment}' still PENDING at row {idx}",
                row_index=idx
            ))
    
    return issues


# ============================================
# ORCHESTRATION: RUN ALL VALIDATIONS PER APP
# ============================================

def validate_single_application(df: pd.DataFrame, app_name: str) -> AppValidationResult:
    """
    Run all validation checks for a single application sheet.
    
    Args:
        df: DataFrame for the application
        app_name: Name of the application
        
    Returns:
        Aggregated AppValidationResult object
    """
    result = AppValidationResult(app_name=app_name)
    
    all_issues: List[ValidationIssue] = []
    all_issues.extend(validate_508_compliance(df, app_name))
    all_issues.extend(validate_sla_configuration(df, app_name))
    all_issues.extend(validate_security_rbac(df, app_name))
    all_issues.extend(validate_integration_points(df, app_name))
    all_issues.extend(validate_deployment_status(df, app_name))
    
    result.issues = all_issues
    result.total_checks = len(df) * 5  # placeholder: 5 categories checked per row
    result.failed_checks = len([i for i in all_issues if i.severity in (Severity.CRITICAL, Severity.HIGH)])
    result.warnings = len([i for i in all_issues if i.severity in (Severity.MEDIUM, Severity.LOW)])
    result.passed_checks = max(0, result.total_checks - result.failed_checks - result.warnings)
    
    return result


def validate_all_applications(filepath: str) -> Dict[str, AppValidationResult]:
    """
    Main orchestration function: load Excel, validate every app sheet.
    
    Args:
        filepath: Path to the master Excel file
        
    Returns:
        Dictionary mapping app_name -> AppValidationResult
    """
    all_sheets = load_application_matrix(filepath)
    app_sheets = filter_known_app_sheets(all_sheets)
    
    results = {}
    for app_name, df in app_sheets.items():
        results[app_name] = validate_single_application(df, app_name)
    
    return results


# ============================================
# REPORTING FUNCTIONS
# ============================================

def generate_summary_report(results: Dict[str, AppValidationResult]) -> pd.DataFrame:
    """
    Generate a summary DataFrame comparing all applications.
    
    Args:
        results: Dictionary of validation results per app
        
    Returns:
        DataFrame with one row per application, summarizing status
    """
    summary_data = []
    
    for app_name, result in results.items():
        summary_data.append({
            'Application': app_name,
            'Status': result.status.value,
            'Pass Rate (%)': result.pass_rate,
            'Total Checks': result.total_checks,
            'Failed': result.failed_checks,
            'Warnings': result.warnings,
            'Critical Issues': len([i for i in result.issues if i.severity == Severity.CRITICAL]),
        })
    
    return pd.DataFrame(summary_data)


def generate_detailed_issues_report(results: Dict[str, AppValidationResult]) -> pd.DataFrame:
    """
    Generate a detailed DataFrame listing every individual issue found.
    
    Args:
        results: Dictionary of validation results per app
        
    Returns:
        DataFrame with one row per issue, across all applications
    """
    issue_data = []
    
    for app_name, result in results.items():
        for issue in result.issues:
            issue_data.append({
                'Application': issue.app_name,
                'Category': issue.category,
                'Severity': issue.severity.value,
                'Message': issue.message,
                'Row Index': issue.row_index if issue.row_index is not None else 'N/A',
            })
    
    if not issue_data:
        return pd.DataFrame(columns=['Application', 'Category', 'Severity', 'Message', 'Row Index'])
    
    df = pd.DataFrame(issue_data)
    
    # Sort by severity (Critical first) then by application name
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    df['_sort_key'] = df['Severity'].map(severity_order)
    df = df.sort_values(['_sort_key', 'Application']).drop(columns=['_sort_key']).reset_index(drop=True)
    
    return df


def print_console_summary(results: Dict[str, AppValidationResult]) -> None:
    """
    Print a human-readable summary to the console.
    
    Args:
        results: Dictionary of validation results per app
    """
    print("=" * 70)
    print("D365 APPLICATION COMPLIANCE VALIDATION SUMMARY")
    print("=" * 70)
    
    for app_name, result in results.items():
        status_symbol = {
            ComplianceStatus.PASS: "✓",
            ComplianceStatus.FAIL: "✗",
            ComplianceStatus.WARNING: "⚠",
            ComplianceStatus.NOT_APPLICABLE: "-"
        }.get(result.status, "?")
        
        print(f"\n{status_symbol} {app_name}")
        print(f"  Status:       {result.status.value}")
        print(f"  Pass Rate:    {result.pass_rate}%")
        print(f"  Failed:       {result.failed_checks}")
        print(f"  Warnings:     {result.warnings}")
        
        # Show top 3 most severe issues for this app
        critical_issues = [i for i in result.issues if i.severity == Severity.CRITICAL]
        if critical_issues:
            print(f"  Critical Issues:")
            for issue in critical_issues[:3]:
                print(f"    • {issue.message}")
            if len(critical_issues) > 3:
                print(f"    ... and {len(critical_issues) - 3} more")
    
    print("\n" + "=" * 70)
    
    # Overall statistics
    total_apps = len(results)
    passing_apps = len([r for r in results.values() if r.status == ComplianceStatus.PASS])
    failing_apps = len([r for r in results.values() if r.status == ComplianceStatus.FAIL])
    warning_apps = len([r for r in results.values() if r.status == ComplianceStatus.WARNING])
    
    print(f"OVERALL: {total_apps} applications validated")
    print(f"  ✓ Passing:  {passing_apps}")
    print(f"  ⚠ Warnings: {warning_apps}")
    print(f"  ✗ Failing:  {failing_apps}")
    print("=" * 70)


# ============================================
# EXPORT FUNCTIONS
# ============================================

def export_reports_to_excel(
    results: Dict[str, AppValidationResult],
    output_path: str = "validation_report.xlsx"
) -> str:
    """
    Export summary and detailed issues to a multi-sheet Excel report.
    
    Args:
        results: Dictionary of validation results per app
        output_path: Where to save the report
        
    Returns:
        Path to the generated report file
    """
    summary_df = generate_summary_report(results)
    issues_df = generate_detailed_issues_report(results)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        issues_df.to_excel(writer, sheet_name='Detailed Issues', index=False)
    
    return output_path


def export_reports_to_json(
    results: Dict[str, AppValidationResult],
    output_path: str = "validation_report.json"
) -> str:
    """
    Export validation results to JSON (useful for CI/CD pipeline consumption).
    
    Args:
        results: Dictionary of validation results per app
        output_path: Where to save the JSON report
        
    Returns:
        Path to the generated JSON file
    """
    import json
    
    output_data = {
        'summary': {
            'total_applications': len(results),
            'passing': len([r for r in results.values() if r.status == ComplianceStatus.PASS]),
            'warnings': len([r for r in results.values() if r.status == ComplianceStatus.WARNING]),
            'failing': len([r for r in results.values() if r.status == ComplianceStatus.FAIL]),
        },
        'applications': {}
    }
    
    for app_name, result in results.items():
        output_data['applications'][app_name] = {
            'status': result.status.value,
            'pass_rate': result.pass_rate,
            'total_checks': result.total_checks,
            'failed_checks': result.failed_checks,
            'warnings': result.warnings,
            'issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity.value,
                    'message': issue.message,
                    'row_index': issue.row_index,
                }
                for issue in result.issues
            ]
        }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    return output_path


def determine_pipeline_exit_code(results: Dict[str, AppValidationResult]) -> int:
    """
    Determine if the CI/CD pipeline should FAIL based on validation results.
    
    Placeholder logic: Pipeline fails if ANY application has CRITICAL issues.
    Adjust this logic based on your actual pipeline gating requirements.
    
    Args:
        results: Dictionary of validation results per app
        
    Returns:
        0 if pipeline should pass, 1 if it should fail
    """
    for result in results.values():
        critical_count = len([i for i in result.issues if i.severity == Severity.CRITICAL])
        if critical_count > 0:
            return 1
    return 0


# ============================================
# MAIN EXECUTION BLOCK
# ============================================

if __name__ == "__main__":  # pragma: no cover
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate D365 application compliance from master Excel file"
    )
    parser.add_argument(
        "filepath",
        nargs="?",
        default="app_compliance_matrix.xlsx",  # TODO: Replace with your default filename
        help="Path to the Excel file containing application data"
    )
    parser.add_argument(
        "--output-dir",
        default="validation_output",
        help="Directory to save reports"
    )
    parser.add_argument(
        "--format",
        choices=["excel", "json", "both"],
        default="both",
        help="Report output format"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("D365 Application Compliance Validator")
    print("=" * 70)
    
    try:
        # Step 1: Load and validate
        print(f"\n📂 Loading file: {args.filepath}")
        results = validate_all_applications(args.filepath)
        print(f"✓ Validated {len(results)} application(s)")
        
        # Step 2: Print console summary
        print_console_summary(results)
        
        # Step 3: Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 4: Export reports
        if args.format in ("excel", "both"):
            excel_path = str(output_dir / "validation_report.xlsx")
            export_reports_to_excel(results, excel_path)
            print(f"\n✓ Excel report saved: {excel_path}")
        
        if args.format in ("json", "both"):
            json_path = str(output_dir / "validation_report.json")
            export_reports_to_json(results, json_path)
            print(f"✓ JSON report saved: {json_path}")
        
        # Step 5: Determine pipeline exit code
        exit_code = determine_pipeline_exit_code(results)
        
        if exit_code == 0:
            print("\n✓ All applications passed critical validation checks")
        else:
            print("\n✗ One or more applications FAILED critical validation checks")
            print("  Pipeline will exit with failure status")
        
        sys.exit(exit_code)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"💡 Tip: Provide a valid Excel file path as an argument:")
        print(f"   python {sys.argv[0]} path/to/your/file.xlsx")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)