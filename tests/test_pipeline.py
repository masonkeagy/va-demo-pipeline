"""
Test suite for VA Demo Pipeline - Data Processing Module
Tests multi-sheet reading, cleaning, calculations, and visualization functions
"""

import pytest
import pandas as pd
import os
from pathlib import Path

from read_data import (
    get_sheet_names,
    read_excel_file,
    read_all_sheets,
    clean_data,
    clean_all_sheets,
    calculate_totals,
    get_numeric_columns,
    preview_sheet,
    preview_all_sheets,
    summarize_sheets,
    plot_null_summary,
    plot_numeric_distribution,
    plot_sheet_comparison,
    generate_all_visualizations,
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def sample_dataframe():
    """Basic single-sheet DataFrame for simple tests."""
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Dave'],
        'Sales': [100, 200, 300, 400],
        'Revenue': [10.5, 20.5, 30.5, 40.5],
    })


@pytest.fixture
def sample_dataframe_with_nulls():
    """DataFrame containing null values for cleaning tests."""
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', None, 'Dave'],
        'Sales': [100, None, 300, 400],
        'Revenue': [10.5, 20.5, 30.5, None],
    })


@pytest.fixture
def multi_sheet_excel_file(tmp_path):
    """
    Creates a temporary multi-sheet Excel file for testing.
    Returns the filepath as a string.
    """
    filepath = tmp_path / "test_data.xlsx"
    
    sheet1 = pd.DataFrame({
        'Requirement ID': ['REQ-001', 'REQ-002', 'REQ-003'],
        'Status': ['Pass', 'Fail', 'Pass'],
        'Score': [95, 60, 88],
    })
    
    sheet2 = pd.DataFrame({
        'Test ID': ['T-001', 'T-002'],
        'Duration': [12.5, 8.3],
        'Result': ['Pass', 'Pass'],
    })
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        sheet1.to_excel(writer, sheet_name='Requirements', index=False)
        sheet2.to_excel(writer, sheet_name='TestCases', index=False)
    
    return str(filepath)


@pytest.fixture
def single_sheet_excel_file(tmp_path):
    """Creates a temporary single-sheet Excel file for basic tests."""
    filepath = tmp_path / "single_sheet.xlsx"
    
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob'],
        'Value': [1, 2],
    })
    
    df.to_excel(filepath, index=False)
    return str(filepath)


@pytest.fixture
def sample_sheets_dict():
    """Dictionary of sheet_name -> DataFrame, mimicking read_all_sheets() output."""
    return {
        'Requirements': pd.DataFrame({
            'ID': ['R1', 'R2', 'R3'],
            'Score': [95, 60, 88],
        }),
        'TestCases': pd.DataFrame({
            'Test': ['T1', 'T2'],
            'Duration': [12.5, 8.3],
        }),
    }


# ============================================
# FILE READING TESTS
# ============================================

class TestFileReading:

    def test_get_sheet_names_returns_correct_sheets(self, multi_sheet_excel_file):
        sheets = get_sheet_names(multi_sheet_excel_file)
        assert sheets == ['Requirements', 'TestCases']

    def test_get_sheet_names_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            get_sheet_names("nonexistent_file.xlsx")

    def test_get_sheet_names_raises_on_invalid_extension(self, tmp_path):
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("not an excel file")
        with pytest.raises(ValueError):
            get_sheet_names(str(bad_file))

    def test_read_excel_file_reads_first_sheet_by_default(self, multi_sheet_excel_file):
        df = read_excel_file(multi_sheet_excel_file)
        assert 'Requirement ID' in df.columns
        assert len(df) == 3

    def test_read_excel_file_reads_specific_sheet(self, multi_sheet_excel_file):
        df = read_excel_file(multi_sheet_excel_file, sheet_name='TestCases')
        assert 'Test ID' in df.columns
        assert len(df) == 2

    def test_read_excel_file_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            read_excel_file("does_not_exist.xlsx")

    def test_read_excel_file_raises_on_invalid_extension(self, tmp_path):
        bad_file = tmp_path / "data.csv"
        bad_file.write_text("a,b,c")
        with pytest.raises(ValueError):
            read_excel_file(str(bad_file))

    def test_read_all_sheets_returns_dict(self, multi_sheet_excel_file):
        sheets = read_all_sheets(multi_sheet_excel_file)
        assert isinstance(sheets, dict)
        assert set(sheets.keys()) == {'Requirements', 'TestCases'}

    def test_read_all_sheets_content_is_correct(self, multi_sheet_excel_file):
        sheets = read_all_sheets(multi_sheet_excel_file)
        assert len(sheets['Requirements']) == 3
        assert len(sheets['TestCases']) == 2
        assert 'Score' in sheets['Requirements'].columns

    def test_read_all_sheets_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            read_all_sheets("missing.xlsx")

    def test_single_sheet_file_reads_correctly(self, single_sheet_excel_file):
        sheets = read_all_sheets(single_sheet_excel_file)
        assert len(sheets) == 1
        assert 'Sheet1' in sheets


# ============================================
# DATA CLEANING TESTS
# ============================================

class TestDataCleaning:

    def test_clean_data_drop_strategy_removes_null_rows(self, sample_dataframe_with_nulls):
        cleaned = clean_data(sample_dataframe_with_nulls, strategy="drop")
        assert len(cleaned) == 1  # Only Alice's row has NO nulls
        assert cleaned.isnull().sum().sum() == 0
        assert cleaned.iloc[0]['Name'] == 'Alice'  # Verify correct row survived

    def test_clean_data_fill_strategy_replaces_nulls_with_zero(self, sample_dataframe_with_nulls):
        cleaned = clean_data(sample_dataframe_with_nulls, strategy="fill")
        assert cleaned.isnull().sum().sum() == 0
        assert len(cleaned) == 4  # No rows removed

    def test_clean_data_invalid_strategy_returns_original(self, sample_dataframe_with_nulls):
        result = clean_data(sample_dataframe_with_nulls, strategy="invalid")
        assert result.equals(sample_dataframe_with_nulls)

    def test_clean_data_resets_index_after_drop(self, sample_dataframe_with_nulls):
        cleaned = clean_data(sample_dataframe_with_nulls, strategy="drop")
        assert list(cleaned.index) == list(range(len(cleaned)))

    def test_clean_data_on_empty_dataframe(self):
        empty_df = pd.DataFrame()
        result = clean_data(empty_df, strategy="drop")
        assert result.empty

    def test_clean_all_sheets_applies_to_every_sheet(self, sample_sheets_dict):
        # Add nulls to test cleaning
        sample_sheets_dict['Requirements'].loc[0, 'Score'] = None
        cleaned = clean_all_sheets(sample_sheets_dict, strategy="drop")
        
        assert len(cleaned) == 2  # Same number of sheets
        assert cleaned['Requirements'].isnull().sum().sum() == 0

    def test_clean_all_sheets_fill_strategy(self, sample_sheets_dict):
        sample_sheets_dict['TestCases'].loc[0, 'Duration'] = None
        cleaned = clean_all_sheets(sample_sheets_dict, strategy="fill")
        
        assert cleaned['TestCases'].isnull().sum().sum() == 0
        assert len(cleaned['TestCases']) == 2  # No rows removed


# ============================================
# CALCULATION TESTS
# ============================================

class TestCalculations:

    def test_calculate_totals_sums_correctly(self, sample_dataframe):
        totals = calculate_totals(sample_dataframe, ['Sales', 'Revenue'])
        assert totals['Sales'] == 1000
        assert totals['Revenue'] == 102.0

    def test_calculate_totals_on_empty_dataframe(self):
        empty_df = pd.DataFrame()
        totals = calculate_totals(empty_df, ['Sales', 'Revenue'])
        assert totals == {'Sales': 0, 'Revenue': 0}

    def test_calculate_totals_handles_missing_column(self, sample_dataframe):
        totals = calculate_totals(sample_dataframe, ['Sales', 'NonExistentColumn'])
        assert totals['Sales'] == 1000
        assert totals['NonExistentColumn'] is None

    def test_calculate_totals_rounds_to_two_decimals(self):
        df = pd.DataFrame({'Value': [1.23456, 2.34567]})
        totals = calculate_totals(df, ['Value'])
        assert totals['Value'] == round(1.23456 + 2.34567, 2)

    def test_calculate_totals_empty_column_list(self, sample_dataframe):
        totals = calculate_totals(sample_dataframe, [])
        assert totals == {}

    def test_get_numeric_columns_identifies_correctly(self, sample_dataframe):
        numeric_cols = get_numeric_columns(sample_dataframe)
        assert 'Sales' in numeric_cols
        assert 'Revenue' in numeric_cols
        assert 'Name' not in numeric_cols

    def test_get_numeric_columns_returns_empty_for_no_numeric_data(self):
        df = pd.DataFrame({'Name': ['Alice', 'Bob'], 'City': ['NY', 'LA']})
        numeric_cols = get_numeric_columns(df)
        assert numeric_cols == []

    def test_get_numeric_columns_on_empty_dataframe(self):
        empty_df = pd.DataFrame()
        numeric_cols = get_numeric_columns(empty_df)
        assert numeric_cols == []


# ============================================
# PREVIEW / SUMMARY TESTS
# ============================================

class TestPreviewAndSummary:

    def test_preview_sheet_runs_without_error(self, sample_dataframe, capsys):
        preview_sheet(sample_dataframe, sheet_name="TestSheet", rows=2)
        captured = capsys.readouterr()
        assert "TestSheet" in captured.out
        assert "Shape:" in captured.out
        assert "Columns:" in captured.out

    def test_preview_sheet_shows_correct_row_count(self, sample_dataframe, capsys):
        preview_sheet(sample_dataframe, sheet_name="Sheet1", rows=5)
        captured = capsys.readouterr()
        assert "4 rows x 3 columns" in captured.out

    def test_preview_sheet_shows_null_counts(self, sample_dataframe_with_nulls, capsys):
        preview_sheet(sample_dataframe_with_nulls, sheet_name="NullSheet")
        captured = capsys.readouterr()
        assert "Null counts per column" in captured.out

    def test_preview_all_sheets_runs_for_every_sheet(self, sample_sheets_dict, capsys):
        preview_all_sheets(sample_sheets_dict, rows=2)
        captured = capsys.readouterr()
        assert "Requirements" in captured.out
        assert "TestCases" in captured.out
        assert "2 sheet(s) found" in captured.out

    def test_summarize_sheets_returns_dataframe(self, sample_sheets_dict):
        summary = summarize_sheets(sample_sheets_dict)
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == 2

    def test_summarize_sheets_has_correct_columns(self, sample_sheets_dict):
        summary = summarize_sheets(sample_sheets_dict)
        expected_cols = ['Sheet Name', 'Rows', 'Columns', 'Total Nulls', 
                          'Numeric Columns', 'Column Names']
        assert list(summary.columns) == expected_cols

    def test_summarize_sheets_reports_correct_row_counts(self, sample_sheets_dict):
        summary = summarize_sheets(sample_sheets_dict)
        req_row = summary[summary['Sheet Name'] == 'Requirements'].iloc[0]
        assert req_row['Rows'] == 3
        assert req_row['Columns'] == 2

    def test_summarize_sheets_counts_numeric_columns_correctly(self, sample_sheets_dict):
        summary = summarize_sheets(sample_sheets_dict)
        req_row = summary[summary['Sheet Name'] == 'Requirements'].iloc[0]
        assert req_row['Numeric Columns'] == 1  # Only 'Score' is numeric

    def test_summarize_sheets_detects_nulls(self, sample_sheets_dict):
        sample_sheets_dict['Requirements'].loc[0, 'Score'] = None
        summary = summarize_sheets(sample_sheets_dict)
        req_row = summary[summary['Sheet Name'] == 'Requirements'].iloc[0]
        assert req_row['Total Nulls'] == 1

    def test_summarize_sheets_on_empty_dict(self):
        summary = summarize_sheets({})
        assert summary.empty


# ============================================
# VISUALIZATION TESTS
# ============================================

class TestVisualizations:

    def test_plot_null_summary_creates_file(self, sample_dataframe_with_nulls, tmp_path):
        output_path = str(tmp_path / "test_nulls.png")
        result = plot_null_summary(sample_dataframe_with_nulls, "TestSheet", output_path)
        
        assert result == output_path
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0  # File is not empty

    def test_plot_null_summary_handles_no_nulls(self, sample_dataframe, tmp_path):
        output_path = str(tmp_path / "test_no_nulls.png")
        result = plot_null_summary(sample_dataframe, "CleanSheet", output_path)
        
        assert result == output_path
        assert Path(output_path).exists()

    def test_plot_null_summary_auto_generates_filename(self, sample_dataframe_with_nulls, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = plot_null_summary(sample_dataframe_with_nulls, "My Sheet Name")
        
        assert "chart_nulls_My_Sheet_Name.png" in result
        assert Path(result).exists()

    def test_plot_numeric_distribution_creates_file(self, sample_dataframe, tmp_path):
        output_path = str(tmp_path / "test_distribution.png")
        result = plot_numeric_distribution(sample_dataframe, "TestSheet", output_path)
        
        assert result == output_path
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_plot_numeric_distribution_returns_none_for_no_numeric_data(self, tmp_path):
        df = pd.DataFrame({'Name': ['Alice', 'Bob'], 'City': ['NY', 'LA']})
        output_path = str(tmp_path / "test_no_numeric.png")
        result = plot_numeric_distribution(df, "NoNumericSheet", output_path)
        
        assert result is None
        assert not Path(output_path).exists()

    def test_plot_numeric_distribution_handles_single_numeric_column(self, tmp_path):
        df = pd.DataFrame({'Name': ['A', 'B', 'C'], 'Value': [1, 2, 3]})
        output_path = str(tmp_path / "test_single_col.png")
        result = plot_numeric_distribution(df, "SingleColSheet", output_path)
        
        assert result == output_path
        assert Path(output_path).exists()

    def test_plot_sheet_comparison_creates_file(self, sample_sheets_dict, tmp_path):
        summary = summarize_sheets(sample_sheets_dict)
        output_path = str(tmp_path / "test_comparison.png")
        result = plot_sheet_comparison(summary, output_path)
        
        assert result == output_path
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_plot_sheet_comparison_default_filename(self, sample_sheets_dict, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        summary = summarize_sheets(sample_sheets_dict)
        result = plot_sheet_comparison(summary)
        
        assert result == "chart_sheet_comparison.png"
        assert Path(result).exists()

    def test_generate_all_visualizations_creates_output_directory(self, sample_sheets_dict, tmp_path):
        output_dir = str(tmp_path / "charts_output")
        generate_all_visualizations(sample_sheets_dict, output_dir=output_dir)
        
        assert Path(output_dir).exists()
        assert Path(output_dir).is_dir()

    def test_generate_all_visualizations_creates_multiple_files(self, sample_sheets_dict, tmp_path):
        output_dir = str(tmp_path / "charts_output")
        chart_files = generate_all_visualizations(sample_sheets_dict, output_dir=output_dir)
        
        assert len(chart_files) > 0
        for chart_path in chart_files:
            assert Path(chart_path).exists()

    def test_generate_all_visualizations_includes_comparison_chart(self, sample_sheets_dict, tmp_path):
        output_dir = str(tmp_path / "charts_output")
        chart_files = generate_all_visualizations(sample_sheets_dict, output_dir=output_dir)
        
        comparison_charts = [f for f in chart_files if 'comparison' in f]
        assert len(comparison_charts) == 1

    def test_generate_all_visualizations_includes_null_charts_for_each_sheet(self, sample_sheets_dict, tmp_path):
        output_dir = str(tmp_path / "charts_output")
        chart_files = generate_all_visualizations(sample_sheets_dict, output_dir=output_dir)
        
        null_charts = [f for f in chart_files if 'nulls' in f]
        assert len(null_charts) == len(sample_sheets_dict)  # One per sheet

    def test_generate_all_visualizations_skips_distribution_for_no_numeric_sheets(self, tmp_path):
        sheets_no_numeric = {
            'TextOnly': pd.DataFrame({'Name': ['A', 'B'], 'City': ['NY', 'LA']})
        }
        output_dir = str(tmp_path / "charts_output")
        chart_files = generate_all_visualizations(sheets_no_numeric, output_dir=output_dir)
        
        distribution_charts = [f for f in chart_files if 'distribution' in f]
        assert len(distribution_charts) == 0

    def test_generate_all_visualizations_handles_empty_sheets_dict(self, tmp_path):
        output_dir = str(tmp_path / "charts_output")
        chart_files = generate_all_visualizations({}, output_dir=output_dir)
        
        # Should still generate the comparison chart (even if empty)
        assert isinstance(chart_files, list)

    def test_plot_numeric_distribution_hides_unused_subplots(self, tmp_path):
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': [7, 8, 9],  # 3 numeric columns = odd number, triggers hidden subplot
        })
        output_path = str(tmp_path / "test_odd_cols.png")
        result = plot_numeric_distribution(df, "OddColsSheet", output_path)

        assert result == output_path
        assert Path(output_path).exists()

    def test_plot_sheet_comparison_with_missing_columns_field(self, tmp_path):
        """Test plot_sheet_comparison when summary_df has Sheet Name but missing Columns."""
        summary = pd.DataFrame({
            'Sheet Name': ['Sheet1'],
            'Rows': [10],
            'Columns': [5],
        })
        output_path = str(tmp_path / "test_comparison_edge.png")
        result = plot_sheet_comparison(summary, output_path)

        assert result == output_path
        assert Path(output_path).exists()


# ============================================
# INTEGRATION TESTS (End-to-End Workflow)
# ============================================

class TestIntegrationWorkflow:

    def test_full_workflow_read_clean_calculate(self, multi_sheet_excel_file):
        """Test the complete pipeline: read -> clean -> calculate."""
        sheets = read_all_sheets(multi_sheet_excel_file)
        cleaned_sheets = clean_all_sheets(sheets, strategy="drop")
        
        totals = calculate_totals(cleaned_sheets['Requirements'], ['Score'])
        assert totals['Score'] > 0

    def test_full_workflow_with_visualizations(self, multi_sheet_excel_file, tmp_path):
        """Test the complete pipeline including chart generation."""
        sheets = read_all_sheets(multi_sheet_excel_file)
        output_dir = str(tmp_path / "output")
        
        chart_files = generate_all_visualizations(sheets, output_dir=output_dir)
        
        assert len(chart_files) > 0
        for chart in chart_files:
            assert Path(chart).exists()

    def test_full_workflow_summary_matches_actual_data(self, multi_sheet_excel_file):
        """Test that summary statistics match the actual underlying data."""
        sheets = read_all_sheets(multi_sheet_excel_file)
        summary = summarize_sheets(sheets)
        
        # Verify Requirements sheet stats match actual DataFrame
        req_summary = summary[summary['Sheet Name'] == 'Requirements'].iloc[0]
        req_actual = sheets['Requirements']
        
        assert req_summary['Rows'] == req_actual.shape[0]
        assert req_summary['Columns'] == req_actual.shape[1]
        assert req_summary['Total Nulls'] == req_actual.isnull().sum().sum()

        # Verify TestCases sheet stats match actual DataFrame
        test_summary = summary[summary['Sheet Name'] == 'TestCases'].iloc[0]
        test_actual = sheets['TestCases']
        
        assert test_summary['Rows'] == test_actual.shape[0]
        assert test_summary['Columns'] == test_actual.shape[1]

    def test_full_workflow_sheet_names_match_across_functions(self, multi_sheet_excel_file):
        """Test that get_sheet_names() and read_all_sheets() return consistent sheet names."""
        names_from_get_sheet_names = set(get_sheet_names(multi_sheet_excel_file))
        names_from_read_all_sheets = set(read_all_sheets(multi_sheet_excel_file).keys())
        
        assert names_from_get_sheet_names == names_from_read_all_sheets

    def test_full_workflow_end_to_end_pipeline(self, multi_sheet_excel_file, tmp_path):
        """
        Complete end-to-end test simulating the main() execution flow:
        read -> preview -> summarize -> clean -> calculate -> visualize
        """
        # Step 1: Discover sheets
        sheet_names = get_sheet_names(multi_sheet_excel_file)
        assert len(sheet_names) == 2

        # Step 2: Load all sheets
        all_sheets = read_all_sheets(multi_sheet_excel_file)
        assert len(all_sheets) == 2

        # Step 3: Summarize
        summary = summarize_sheets(all_sheets)
        assert len(summary) == 2

        # Step 4: Clean
        cleaned_sheets = clean_all_sheets(all_sheets, strategy="drop")
        assert len(cleaned_sheets) == len(all_sheets)

        # Step 5: Calculate totals
        for sheet_name, df in all_sheets.items():
            numeric_cols = get_numeric_columns(df)
            if numeric_cols:
                totals = calculate_totals(df, numeric_cols)
                assert isinstance(totals, dict)
                assert len(totals) == len(numeric_cols)

        # Step 6: Generate visualizations
        output_dir = str(tmp_path / "final_output")
        chart_files = generate_all_visualizations(all_sheets, output_dir=output_dir)
        assert len(chart_files) > 0
        
        # Verify all chart files actually exist on disk
        for chart_path in chart_files:
            assert Path(chart_path).exists()
            assert Path(chart_path).stat().st_size > 0


# ============================================
# EDGE CASE TESTS
# ============================================

class TestEdgeCases:

    def test_excel_file_with_single_row(self, tmp_path):
        """Test handling of a sheet with only one row of data."""
        filepath = tmp_path / "single_row.xlsx"
        df = pd.DataFrame({'Name': ['Alice'], 'Value': [100]})
        df.to_excel(filepath, index=False)
        
        sheets = read_all_sheets(str(filepath))
        assert len(sheets['Sheet1']) == 1

    def test_excel_file_with_all_null_column(self, tmp_path):
        """Test handling of a column that is entirely null."""
        filepath = tmp_path / "all_null.xlsx"
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob'],
            'EmptyCol': [None, None]
        })
        df.to_excel(filepath, index=False)
        
        sheets = read_all_sheets(str(filepath))
        cleaned = clean_data(sheets['Sheet1'], strategy="drop")
        assert cleaned.empty  # All rows removed since EmptyCol is always null

    def test_excel_file_with_special_characters_in_sheet_name(self, tmp_path):
        """Test handling of sheet names with spaces and special characters."""
        filepath = tmp_path / "special_names.xlsx"
        df = pd.DataFrame({'A': [1, 2]})
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='My Sheet (2024)', index=False)
        
        sheets = read_all_sheets(str(filepath))
        assert 'My Sheet (2024)' in sheets

    def test_visualization_with_special_characters_in_sheet_name(self, tmp_path):
        """Test that chart generation handles special characters in sheet names safely."""
        df = pd.DataFrame({'Value': [1, 2, 3, None]})
        output_dir = str(tmp_path / "charts")
        
        sheets = {'My Sheet (2024)/Test': df}
        chart_files = generate_all_visualizations(sheets, output_dir=output_dir)
        
        assert len(chart_files) > 0
        for chart_path in chart_files:
            assert Path(chart_path).exists()

    def test_large_number_of_sheets(self, tmp_path):
        """Test handling of an Excel file with many sheets (stress test)."""
        filepath = tmp_path / "many_sheets.xlsx"
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for i in range(10):
                df = pd.DataFrame({'Col': [i, i+1, i+2]})
                df.to_excel(writer, sheet_name=f'Sheet{i}', index=False)
        
        sheets = read_all_sheets(str(filepath))
        assert len(sheets) == 10

    def test_calculate_totals_with_negative_numbers(self):
        """Test that totals calculation handles negative values correctly."""
        df = pd.DataFrame({'Value': [-10, 20, -5, 15]})
        totals = calculate_totals(df, ['Value'])
        assert totals['Value'] == 20

    def test_clean_data_preserves_correct_dtypes_after_fill(self):
        """Test that fill strategy doesn't corrupt numeric column dtypes."""
        df = pd.DataFrame({'Value': [1.5, None, 3.5]})
        cleaned = clean_data(df, strategy="fill")
        assert cleaned['Value'].dtype in ['float64', 'int64']


# ============================================
# PYTEST CONFIGURATION
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])