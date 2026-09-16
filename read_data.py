"""
VA Demo Pipeline - Data Processing Module
Enhanced with multi-sheet support and data visualization
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for pipeline/server use
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional


# ============================================
# FILE READING FUNCTIONS
# ============================================

def get_sheet_names(filepath: str) -> List[str]:
    """
    Get all sheet names from an Excel file without loading data.
    
    Args:
        filepath: Path to the Excel file
        
    Returns:
        List of sheet names
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not an Excel file
    """
    _validate_excel_file(filepath)
    excel_file = pd.ExcelFile(filepath)
    return excel_file.sheet_names


def read_excel_file(filepath: str, sheet_name: str = None) -> pd.DataFrame:
    """
    Read a single sheet from an Excel file and return a DataFrame.
    
    Args:
        filepath: Path to the Excel file
        sheet_name: Specific sheet to read. If None, reads the first sheet.
        
    Returns:
        pandas DataFrame containing the data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not an Excel file
    """
    _validate_excel_file(filepath)
    
    if sheet_name:
        df = pd.read_excel(filepath, sheet_name=sheet_name)
    else:
        df = pd.read_excel(filepath)
    
    return df


def read_all_sheets(filepath: str) -> Dict[str, pd.DataFrame]:
    """
    Read ALL sheets from an Excel file into a dictionary of DataFrames.
    
    Args:
        filepath: Path to the Excel file
        
    Returns:
        Dictionary where keys are sheet names and values are DataFrames
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not an Excel file
    """
    _validate_excel_file(filepath)
    
    all_sheets = pd.read_excel(filepath, sheet_name=None)
    return all_sheets


def _validate_excel_file(filepath: str) -> None:
    """Internal helper to validate Excel file exists and has correct extension."""
    if not filepath.endswith(('.xlsx', '.xls')):
        raise ValueError(f"File must be Excel format: {filepath}")
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"File not found: {filepath}")


# ============================================
# DATA CLEANING FUNCTIONS
# ============================================

def clean_data(df: pd.DataFrame, strategy: str = "drop") -> pd.DataFrame:
    """
    Clean null values from DataFrame.
    
    Args:
        df: Input DataFrame
        strategy: 'drop' to remove rows with nulls, 'fill' to fill with 0
        
    Returns:
        Cleaned DataFrame
    """
    if strategy == "drop":
        return df.dropna().reset_index(drop=True)
    elif strategy == "fill":
        return df.fillna(0)
    return df


def clean_all_sheets(sheets: Dict[str, pd.DataFrame], strategy: str = "drop") -> Dict[str, pd.DataFrame]:
    """
    Apply cleaning to all sheets in a dictionary.
    
    Args:
        sheets: Dictionary of sheet_name -> DataFrame
        strategy: 'drop' or 'fill'
        
    Returns:
        Dictionary of cleaned DataFrames
    """
    return {name: clean_data(df, strategy) for name, df in sheets.items()}


# ============================================
# CALCULATION FUNCTIONS
# ============================================

def calculate_totals(df: pd.DataFrame, columns: list) -> dict:
    """
    Calculate sum totals for specified columns.
    
    Args:
        df: Input DataFrame
        columns: List of column names to sum
        
    Returns:
        Dictionary with column totals
    """
    if df.empty:
        return dict.fromkeys(columns, 0)
    
    totals = {}
    for col in columns:
        if col in df.columns:
            totals[col] = round(df[col].sum(), 2)
        else:
            totals[col] = None  # Column doesn't exist
    
    return totals


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Identify all numeric columns in a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        List of column names that contain numeric data
    """
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()


# ============================================
# EXPLORATION / PREVIEW FUNCTIONS
# ============================================

def preview_sheet(df: pd.DataFrame, sheet_name: str = "Sheet", rows: int = 5) -> None:
    """
    Print a preview of a DataFrame (head, shape, columns, dtypes).
    
    Args:
        df: DataFrame to preview
        sheet_name: Name of the sheet (for display purposes)
        rows: Number of rows to show in head
    """
    print(f"\n{'=' * 60}")
    print(f"Sheet: {sheet_name}")
    print(f"{'=' * 60}")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nData Types:\n{df.dtypes}")
    print(f"\nHead ({rows} rows):")
    print(df.head(rows).to_string())
    print(f"\nNull counts per column:")
    print(df.isnull().sum().to_string())


def preview_all_sheets(sheets: Dict[str, pd.DataFrame], rows: int = 5) -> None:
    """
    Print a preview of every sheet in a dictionary of DataFrames.
    
    Args:
        sheets: Dictionary of sheet_name -> DataFrame
        rows: Number of rows to show per sheet
    """
    print(f"\n{'#' * 60}")
    print(f"# EXCEL FILE OVERVIEW - {len(sheets)} sheet(s) found")
    print(f"{'#' * 60}")
    
    for sheet_name, df in sheets.items():
        preview_sheet(df, sheet_name, rows)


def summarize_sheets(sheets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Create a summary table comparing all sheets (rows, columns, nulls).
    
    Args:
        sheets: Dictionary of sheet_name -> DataFrame
        
    Returns:
        DataFrame summarizing each sheet's basic stats
    """
    summary_data = []
    
    for sheet_name, df in sheets.items():
        summary_data.append({
            'Sheet Name': sheet_name,
            'Rows': df.shape[0],
            'Columns': df.shape[1],
            'Total Nulls': df.isnull().sum().sum(),
            'Numeric Columns': len(get_numeric_columns(df)),
            'Column Names': ', '.join(df.columns[:5]) + ('...' if len(df.columns) > 5 else '')
        })
    
    return pd.DataFrame(summary_data)


# ============================================
# VISUALIZATION FUNCTIONS
# ============================================

def plot_null_summary(df: pd.DataFrame, sheet_name: str = "Sheet", output_path: str = None) -> str:
    """
    Create a bar chart showing null value counts per column.
    
    Args:
        df: Input DataFrame
        sheet_name: Name of the sheet (for title)
        output_path: Where to save the chart. If None, auto-generates name.
        
    Returns:
        Path to the saved chart image
    """
    if output_path is None:
        safe_name = sheet_name.replace(' ', '_').replace('/', '_')
        output_path = f"chart_nulls_{safe_name}.png"
    
    null_counts = df.isnull().sum()
    null_counts = null_counts[null_counts > 0]  # Only show columns WITH nulls
    
    plt.figure(figsize=(10, 6))
    
    if null_counts.empty:
        plt.text(0.5, 0.5, 'No Null Values Found!', 
                  horizontalalignment='center', verticalalignment='center',
                  fontsize=16, transform=plt.gca().transAxes)
    else:
        null_counts.plot(kind='bar', color='salmon')
        plt.ylabel('Null Count')
        plt.xticks(rotation=45, ha='right')
    
    plt.title(f'Null Values by Column - {sheet_name}')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()
    
    return output_path


def plot_numeric_distribution(df: pd.DataFrame, sheet_name: str = "Sheet", output_path: str = None) -> Optional[str]:
    """
    Create histograms for all numeric columns in a DataFrame.
    
    Args:
        df: Input DataFrame
        sheet_name: Name of the sheet (for title)
        output_path: Where to save the chart. If None, auto-generates name.
        
    Returns:
        Path to the saved chart image, or None if no numeric columns exist
    """
    numeric_cols = get_numeric_columns(df)
    
    if not numeric_cols:
        return None
    
    if output_path is None:
        safe_name = sheet_name.replace(' ', '_').replace('/', '_')
        output_path = f"chart_distribution_{safe_name}.png"
    
    num_plots = len(numeric_cols)
    fig, axes = plt.subplots(nrows=(num_plots + 1) // 2, ncols=2, figsize=(12, 4 * ((num_plots + 1) // 2)))
    axes = axes.flatten() if num_plots > 1 else [axes]
    
    for idx, col in enumerate(numeric_cols):
        df[col].dropna().plot(kind='hist', ax=axes[idx], bins=20, color='steelblue', edgecolor='black')
        axes[idx].set_title(f'{col}')
        axes[idx].set_xlabel(col)
    
    # Hide unused subplots
    for idx in range(num_plots, len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle(f'Numeric Distributions - {sheet_name}')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()
    
    return output_path


def plot_sheet_comparison(summary_df: pd.DataFrame, output_path: str = "chart_sheet_comparison.png") -> str:
    """
    Create a comparison bar chart showing rows/columns across all sheets.
    
    Args:
        summary_df: DataFrame from summarize_sheets() function
        output_path: Where to save the chart
        
    Returns:
        Path to the saved chart image
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chart 1: Row counts per sheet
    ax1.bar(summary_df['Sheet Name'], summary_df['Rows'], color='steelblue')
    ax1.set_title('Row Count by Sheet')
    ax1.set_ylabel('Number of Rows')
    ax1.set_xlabel('Sheet Name')
    ax1.tick_params(axis='x', rotation=45)
    
    # Chart 2: Column counts per sheet
    ax2.bar(summary_df['Sheet Name'], summary_df['Columns'], color='mediumseagreen')
    ax2.set_title('Column Count by Sheet')
    ax2.set_ylabel('Number of Columns')
    ax2.set_xlabel('Sheet Name')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Excel File - Sheet Comparison Overview')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()
    
    return output_path


def generate_all_visualizations(sheets: Dict[str, pd.DataFrame], output_dir: str = ".") -> List[str]:
    """
    Generate all available visualizations for every sheet in the Excel file.
    
    Args:
        sheets: Dictionary of sheet_name -> DataFrame
        output_dir: Directory to save all chart images
        
    Returns:
        List of file paths for all generated charts
    """
    output_path_obj = Path(output_dir)
    output_path_obj.mkdir(parents=True, exist_ok=True)
    
    generated_files = []
    
    # 1. Sheet comparison chart (rows/columns across all sheets)
    summary_df = summarize_sheets(sheets)
    comparison_path = str(output_path_obj / "chart_sheet_comparison.png")
    generated_files.append(plot_sheet_comparison(summary_df, comparison_path))
    
    # 2. Per-sheet null value charts
    for sheet_name, df in sheets.items():
        safe_name = sheet_name.replace(' ', '_').replace('/', '_')
        null_path = str(output_path_obj / f"chart_nulls_{safe_name}.png")
        generated_files.append(plot_null_summary(df, sheet_name, null_path))
    
    # 3. Per-sheet numeric distribution charts (only if numeric data exists)
    for sheet_name, df in sheets.items():
        safe_name = sheet_name.replace(' ', '_').replace('/', '_')
        dist_path = str(output_path_obj / f"chart_distribution_{safe_name}.png")
        result = plot_numeric_distribution(df, sheet_name, dist_path)
        if result:
            generated_files.append(result)
    
    return generated_files


# ============================================
# MAIN EXECUTION BLOCK
# ============================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("VA Demo Pipeline - Data Processing Module")
    print("=" * 60)
    
    # Get filepath from command line argument, or use default
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "data.xlsx"  # Default - change as needed
    
    try:
        # ============================================
        # Step 1: Discover sheet structure
        # ============================================
        print(f"\n📂 Reading file: {filepath}")
        sheet_names = get_sheet_names(filepath)
        print(f"✓ Found {len(sheet_names)} sheet(s): {sheet_names}")
        
        # ============================================
        # Step 2: Load all sheets
        # ============================================
        print(f"\n📊 Loading all sheets into memory...")
        all_sheets = read_all_sheets(filepath)
        print(f"✓ All sheets loaded successfully")
        
        # ============================================
        # Step 3: Preview each sheet (head, dtypes, nulls)
        # ============================================
        preview_all_sheets(all_sheets, rows=5)
        
        # ============================================
        # Step 4: Generate summary comparison table
        # ============================================
        print(f"\n{'=' * 60}")
        print("SHEET SUMMARY COMPARISON")
        print(f"{'=' * 60}")
        summary = summarize_sheets(all_sheets)
        print(summary.to_string(index=False))
        
        # ============================================
        # Step 5: Clean data (optional - drop nulls)
        # ============================================
        print(f"\n🧹 Cleaning data (strategy='drop')...")
        cleaned_sheets = clean_all_sheets(all_sheets, strategy="drop")
        for name, df in cleaned_sheets.items():
            original_rows = all_sheets[name].shape[0]
            cleaned_rows = df.shape[0]
            print(f"  • {name}: {original_rows} → {cleaned_rows} rows "
                  f"({original_rows - cleaned_rows} removed)")
        
        # ============================================
        # Step 6: Calculate totals for numeric columns
        # ============================================
        print(f"\n💰 Calculating totals for numeric columns...")
        for sheet_name, df in all_sheets.items():
            numeric_cols = get_numeric_columns(df)
            if numeric_cols:
                totals = calculate_totals(df, numeric_cols)
                print(f"\n  Sheet: {sheet_name}")
                for col, total in totals.items():
                    print(f"    • {col}: {total}")
            else:
                print(f"\n  Sheet: {sheet_name} - No numeric columns found")
        
        # ============================================
        # Step 7: Generate visualizations
        # ============================================
        print(f"\n📈 Generating visualizations...")
        chart_files = generate_all_visualizations(all_sheets, output_dir="output_charts")
        print(f"✓ Generated {len(chart_files)} chart(s):")
        for chart in chart_files:
            print(f"  • {chart}")
        
        print(f"\n{'=' * 60}")
        print("✓ Processing complete!")
        print(f"{'=' * 60}")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"💡 Tip: Provide a valid Excel file path as an argument:")
        print(f"   python read_data.py path/to/your/file.xlsx")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)