"""
VA Demo Pipeline - Data Processing Module
"""

import pandas as pd
from pathlib import Path

def read_excel_file(filepath: str) -> pd.DataFrame:
    """
    Read an Excel file and return a DataFrame.
    
    Args:
        filepath: Path to the Excel file
        
    Returns:
        pandas DataFrame containing the data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not an Excel file
    """
    if not filepath.endswith(('.xlsx', '.xls')):
        raise ValueError(f"File must be Excel format: {filepath}")
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_excel(filepath)
    return df


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
    
    return {col: round(df[col].sum(), 2) for col in columns}


if __name__ == "__main__":
    print("VA Demo Pipeline - Ready to process data")