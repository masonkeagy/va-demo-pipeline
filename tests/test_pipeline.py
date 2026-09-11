# test_data_processing.py
# Run all tests
# pytest test_data_processing.py -v

# Run with coverage
# pytest test_data_processing.py -v --tb=short --cov=. --cov-report=term-missing

# Run a single class
# pytest test_data_processing.py::TestCleanNulls -v

# Run only parametrized tests
# pytest test_data_processing.py -v -k "parametrized"
"""
Unit tests for basic data processing functions:
- Reading data
- Cleaning nulls
- Calculating totals
Uses: pytest
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open, MagicMock
import io
import json


# ============================================================
# SOURCE FUNCTIONS UNDER TEST (data_processing.py simulation)
# ============================================================

def read_data(filepath: str) -> pd.DataFrame:
    """Read CSV data from a given filepath."""
    if not filepath.endswith(".csv"):
        raise ValueError(f"Unsupported file format: {filepath}")
    return pd.read_csv(filepath)


def read_data_from_dict(data: dict) -> pd.DataFrame:
    """Create a DataFrame directly from a dictionary."""
    if not isinstance(data, dict):
        raise TypeError("Input must be a dictionary.")
    if not data:
        raise ValueError("Input dictionary cannot be empty.")
    return pd.DataFrame(data)


def clean_nulls(df: pd.DataFrame, strategy: str = "drop", fill_value=0) -> pd.DataFrame:
    """
    Clean null values from a DataFrame.
    strategy:
        'drop'  → drop rows with any null
        'fill'  → fill nulls with fill_value
        'mean'  → fill numeric nulls with column mean
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if df.empty:
        return df
    if strategy == "drop":
        return df.dropna().reset_index(drop=True)
    elif strategy == "fill":
        return df.fillna(fill_value)
    elif strategy == "mean":
        return df.fillna(df.mean(numeric_only=True))
    else:
        raise ValueError(f"Unknown strategy: '{strategy}'. Choose 'drop', 'fill', or 'mean'.")


def calculate_totals(df: pd.DataFrame, columns: list) -> dict:
    """
    Calculate the sum of specified numeric columns.
    Returns a dict: {column_name: total}
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if df.empty:
        return {col: 0 for col in columns}
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise KeyError(f"Columns not found in DataFrame: {missing}")
    non_numeric = [col for col in columns if not pd.api.types.is_numeric_dtype(df[col])]
    if non_numeric:
        raise TypeError(f"Non-numeric columns cannot be summed: {non_numeric}")
    return {col: round(df[col].sum(), 2) for col in columns}


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def sample_df():
    """A clean DataFrame with no nulls."""
    return pd.DataFrame({
        "id":       [1,    2,    3,    4,    5   ],
        "name":     ["Alice","Bob","Carol","Dave","Eve"],
        "sales":    [200.0, 150.0, 300.0, 100.0, 250.0],
        "expenses": [80.0,  60.0,  120.0, 40.0,  90.0 ],
        "units":    [10,    8,     15,    5,     12   ],
    })


@pytest.fixture
def dirty_df():
    """A DataFrame that contains null values."""
    return pd.DataFrame({
        "id":       [1,    2,    3,    None, 5   ],
        "name":     ["Alice", None, "Carol", "Dave", "Eve"],
        "sales":    [200.0, None, 300.0, 100.0, None ],
        "expenses": [80.0,  60.0, None,  40.0,  90.0 ],
        "units":    [10,    8,    15,    None,  12   ],
    })


@pytest.fixture
def single_row_df():
    """A single-row DataFrame."""
    return pd.DataFrame({
        "sales":    [500.0],
        "expenses": [200.0],
        "units":    [25],
    })


@pytest.fixture
def empty_df():
    """An empty DataFrame."""
    return pd.DataFrame({"sales": [], "expenses": [], "units": []})


@pytest.fixture
def large_df():
    """A large DataFrame for performance/edge-case tests."""
    rng = np.random.default_rng(seed=42)
    n = 10_000
    data = {
        "id":       np.arange(1, n + 1),
        "sales":    rng.uniform(50, 5000, n).round(2),
        "expenses": rng.uniform(10, 2000, n).round(2),
        "units":    rng.integers(1, 500, n),
    }
    return pd.DataFrame(data)


# ============================================================
# TESTS — read_data()
# ============================================================

class TestReadData:
    """Tests for the read_data() function."""

    def test_read_valid_csv(self, sample_df, tmp_path):
        """Should successfully read a valid CSV file."""
        csv_file = tmp_path / "test.csv"
        sample_df.to_csv(csv_file, index=False)

        result = read_data(str(csv_file))

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_read_csv_row_count(self, sample_df, tmp_path):
        """Row count should match the original DataFrame."""
        csv_file = tmp_path / "test.csv"
        sample_df.to_csv(csv_file, index=False)

        result = read_data(str(csv_file))

        assert len(result) == len(sample_df)

    def test_read_csv_column_names(self, sample_df, tmp_path):
        """Column names should be preserved after reading."""
        csv_file = tmp_path / "test.csv"
        sample_df.to_csv(csv_file, index=False)

        result = read_data(str(csv_file))

        assert list(result.columns) == list(sample_df.columns)

    def test_read_csv_data_integrity(self, sample_df, tmp_path):
        """Data values should be identical to the original."""
        csv_file = tmp_path / "test.csv"
        sample_df.to_csv(csv_file, index=False)

        result = read_data(str(csv_file))

        pd.testing.assert_frame_equal(result, sample_df)

    def test_read_unsupported_format_raises_value_error(self):
        """Reading a non-CSV file should raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            read_data("data.xlsx")

    def test_read_missing_file_raises_error(self):
        """Reading a non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_data("non_existent_file.csv")

    def test_read_empty_csv(self, tmp_path):
        """An empty CSV (headers only) should return an empty DataFrame."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("sales,expenses,units\n")

        result = read_data(str(csv_file))

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert list(result.columns) == ["sales", "expenses", "units"]


class TestReadDataFromDict:
    """Tests for the read_data_from_dict() function."""

    def test_valid_dict_returns_dataframe(self):
        """A valid dict should return a DataFrame."""
        data = {"a": [1, 2, 3], "b": [4, 5, 6]}
        result = read_data_from_dict(data)
        assert isinstance(result, pd.DataFrame)

    def test_dict_shape_matches(self):
        """DataFrame shape should match the input dict dimensions."""
        data = {"x": [10, 20], "y": [30, 40], "z": [50, 60]}
        result = read_data_from_dict(data)
        assert result.shape == (2, 3)

    def test_dict_column_names_preserved(self):
        """Column names should match dict keys."""
        data = {"col1": [1], "col2": [2], "col3": [3]}
        result = read_data_from_dict(data)
        assert list(result.columns) == ["col1", "col2", "col3"]

    def test_non_dict_raises_type_error(self):
        """Passing a non-dict should raise TypeError."""
        with pytest.raises(TypeError, match="Input must be a dictionary"):
            read_data_from_dict([1, 2, 3])

    def test_empty_dict_raises_value_error(self):
        """Passing an empty dict should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            read_data_from_dict({})

    def test_dict_with_none_values(self):
        """Dict with None values should create a DataFrame with NaN."""
        data = {"a": [1, None, 3], "b": [None, 5, 6]}
        result = read_data_from_dict(data)
        assert result.isnull().values.any()

    @pytest.mark.parametrize("input_data, expected_shape", [
        ({"a": [1]},                        (1, 1)),
        ({"a": [1, 2], "b": [3, 4]},        (2, 2)),
        ({"x": list(range(100))},           (100, 1)),
    ])
    def test_various_dict_shapes(self, input_data, expected_shape):
        """Parametrized: various shapes should produce correct DataFrames."""
        result = read_data_from_dict(input_data)
        assert result.shape == expected_shape


# ============================================================
# TESTS — clean_nulls()
# ============================================================

class TestCleanNulls:
    """Tests for the clean_nulls() function."""

    # --- strategy: drop ---

    def test_drop_removes_null_rows(self, dirty_df):
        """Drop strategy should remove every row that has at least one null."""
        result = clean_nulls(dirty_df, strategy="drop")
        assert result.isnull().sum().sum() == 0

    def test_drop_reduces_row_count(self, dirty_df):
        """Drop strategy should yield fewer rows than the dirty DataFrame."""
        result = clean_nulls(dirty_df, strategy="drop")
        assert len(result) < len(dirty_df)

    def test_drop_keeps_clean_rows_intact(self, dirty_df):
        """Rows without nulls should survive the drop strategy."""
        result = clean_nulls(dirty_df, strategy="drop")
        assert len(result) > 0

    def test_drop_on_clean_df_unchanged(self, sample_df):
        """Applying drop on a clean DataFrame should return it unchanged."""
        result = clean_nulls(sample_df, strategy="drop")
        pd.testing.assert_frame_equal(result.reset_index(drop=True),
                                      sample_df.reset_index(drop=True))

    # --- strategy: fill ---

    def test_fill_zero_removes_all_nulls(self, dirty_df):
        """Fill-zero strategy should leave no nulls."""
        result = clean_nulls(dirty_df, strategy="fill", fill_value=0)
        assert result.isnull().sum().sum() == 0

    def test_fill_preserves_row_count(self, dirty_df):
        """Fill strategy must NOT remove rows."""
        result = clean_nulls(dirty_df, strategy="fill", fill_value=0)
        assert len(result) == len(dirty_df)

    def test_fill_custom_value(self, dirty_df):
        """Fill strategy should replace nulls with the provided fill_value."""
        result = clean_nulls(dirty_df, strategy="fill", fill_value=-1)
        assert result.isnull().sum().sum() == 0
        # Numeric cells that were NaN should now hold -1
        assert (result["sales"] == -1).any()

    def test_fill_string_value(self):
        """Fill strategy should work with a string fill value for object cols."""
        df = pd.DataFrame({"name": ["Alice", None, "Carol"],
                           "score": [90, None, 85]})
        result = clean_nulls(df, strategy="fill", fill_value="UNKNOWN")
        assert "UNKNOWN" in result["name"].values

    # --- strategy: mean ---

    def test_mean_fill_removes_numeric_nulls(self, dirty_df):
        """Mean strategy should remove nulls in numeric columns."""
        result = clean_nulls(dirty_df, strategy="mean")
        numeric_cols = dirty_df.select_dtypes(include="number").columns
        assert result[numeric_cols].isnull().sum().sum() == 0

    def test_mean_fill_preserves_row_count(self, dirty_df):
        """Mean strategy must NOT drop rows."""
        result = clean_nulls(dirty_df, strategy="mean")
        assert len(result) == len(dirty_df)

    def test_mean_fill_correct_value(self):
        """Mean-filled values should exactly equal the column mean."""
        df = pd.DataFrame({"sales": [100.0, None, 200.0]})
        result = clean_nulls(df, strategy="mean")
        expected_mean = 150.0
        assert result.loc[1, "sales"] == pytest.approx(expected_mean)

    # --- edge cases ---

    def test_empty_df_returns_empty(self, empty_df):
        """Cleaning an empty DataFrame should return an empty DataFrame."""
        result = clean_nulls(empty_df, strategy="drop")
        assert result.empty

    def test_invalid_strategy_raises_value_error(self, sample_df):
        """An unknown strategy should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            clean_nulls(sample_df, strategy="interpolate")

    def test_non_dataframe_raises_type_error(self):
        """Passing a non-DataFrame should raise TypeError."""
        with pytest.raises(TypeError, match="pandas DataFrame"):
            clean_nulls({"a": [1, None]}, strategy="drop")

    @pytest.mark.parametrize("strategy,fill_value", [
        ("drop",  0),
        ("fill",  0),
        ("fill", -999),
        ("mean",  0),
    ])
    def test_no_nulls_after_cleaning(self, dirty_df, strategy, fill_value):
        """Parametrized: all strategies should eliminate nulls (numeric)."""
        result = clean_nulls(dirty_df, strategy=strategy, fill_value=fill_value)
        numeric_cols = dirty_df.select_dtypes(include="number").columns
        assert result[numeric_cols].isnull().sum().sum() == 0


# ============================================================
# TESTS — calculate_totals()
# ============================================================

class TestCalculateTotals:
    """Tests for the calculate_totals() function."""

    # --- basic correctness ---

    def test_returns_dict(self, sample_df):
        """calculate_totals should return a dictionary."""
        result = calculate_totals(sample_df, ["sales"])
        assert isinstance(result, dict)

    def test_single_column_total(self, sample_df):
        """Total of 'sales' should equal the manual sum."""
        result = calculate_totals(sample_df, ["sales"])
        expected = round(sample_df["sales"].sum(), 2)
        assert result["sales"] == pytest.approx(expected)

    def test_multiple_columns_totals(self, sample_df):
        """Totals for multiple columns should all be correct."""
        cols = ["sales", "expenses", "units"]
        result = calculate_totals(sample_df, cols)

        assert result["sales"]    == pytest.approx(round(sample_df["sales"].sum(),    2))
        assert result["expenses"] == pytest.approx(round(sample_df["expenses"].sum(), 2))
        assert result["units"]    == pytest.approx(round(sample_df["units"].sum(),    2))

    def test_result_keys_match_requested_columns(self, sample_df):
        """The result dict should have exactly the requested column keys."""
        cols = ["sales", "expenses"]
        result = calculate_totals(sample_df, cols)
        assert set(result.keys()) == set(cols)

    def test_single_row_total(self, single_row_df):
        """Single-row DataFrame total should equal the single value."""
        result = calculate_totals(single_row_df, ["sales"])
        assert result["sales"] == pytest.approx(500.0)

    def test_empty_df_returns_zeros(self, empty_df):
        """An empty DataFrame should return 0 for every requested column."""
        result = calculate_totals(empty_df, ["sales", "expenses"])
        assert result == {"sales": 0, "expenses": 0}

    # --- numerical precision ---

    def test_result_is_rounded_to_two_decimals(self):
        """Totals should be rounded to 2 decimal places."""
        df = pd.DataFrame({"price": [1.005, 2.005, 3.005]})
        result = calculate_totals(df, ["price"])
        # verify it's a float with at most 2 decimal places
        assert result["price"] == round(result["price"], 2)

    def test_total_with_large_dataset(self, large_df):
        """Totals on a 10k-row dataset should match pandas sum."""
        cols = ["sales", "expenses", "units"]
        result = calculate_totals(large_df, cols)
        for col in cols:
            assert result[col] == pytest.approx(round(large_df[col].sum(), 2), rel=1e-5)

    def test_total_with_negative_values(self):
        """Totals should handle negative numbers correctly."""
        df = pd.DataFrame({"profit": [100.0, -50.0, -30.0, 20.0]})
        result = calculate_totals(df, ["profit"])
        assert result["profit"] == pytest.approx(40.0)

    def test_total_with_zeros(self):
        """Totals should handle all-zero columns."""
        df = pd.DataFrame({"sales": [0, 0, 0, 0]})
        result = calculate_totals(df, ["sales"])
        assert result["sales"] == pytest.approx(0.0)

    def test_total_with_float_precision(self):
        """Floating-point sums should be correct within tolerance."""
        df = pd.DataFrame({"amount": [0.1, 0.2, 0.3]})
        result = calculate_totals(df, ["amount"])
        assert result["amount"] == pytest.approx(0.6, abs=1e-9)

    # --- error handling ---

    def test_missing_column_raises_key_error(self, sample_df):
        """Requesting a non-existent column should raise KeyError."""
        with pytest.raises(KeyError, match="Columns not found"):
            calculate_totals(sample_df, ["nonexistent_col"])

    def test_non_numeric_column_raises_type_error(self, sample_df):
        """Requesting a non-numeric column should raise TypeError."""
        with pytest.raises(TypeError, match="Non-numeric columns"):
            calculate_totals(sample_df, ["name"])

    def test_non_dataframe_input_raises_type_error(self):
        """Passing a non-DataFrame should raise TypeError."""
        with pytest.raises(TypeError, match="pandas DataFrame"):
            calculate_totals({"sales": [100, 200]}, ["sales"])

    # --- integration-style (pipeline) ---

    def test_pipeline_clean_then_total(self, dirty_df):
        """Full pipeline: clean nulls → calculate totals should work end-to-end."""
        cleaned  = clean_nulls(dirty_df, strategy="fill", fill_value=0)
        result   = calculate_totals(cleaned, ["sales", "expenses"])
        assert isinstance(result, dict)
        assert result["sales"]    >= 0
        assert result["expenses"] >= 0

    def test_pipeline_drop_then_total_matches_manual(self, dirty_df):
        """After drop-cleaning, the manual sum should equal calculate_totals."""
        cleaned  = clean_nulls(dirty_df, strategy="drop")
        result   = calculate_totals(cleaned, ["sales"])
        expected = round(cleaned["sales"].sum(), 2)
        assert result["sales"] == pytest.approx(expected)

    @pytest.mark.parametrize("values,expected_total", [
        ([10, 20, 30],          60.0),
        ([0, 0, 0],              0.0),
        ([-10, 10, -10],       -10.0),
        ([1_000_000, 2_000_000], 3_000_000.0),
        ([0.001, 0.002, 0.003],  0.006),
    ])
    def test_parametrized_totals(self, values, expected_total):
        """Parametrized: various value ranges should compute the correct total."""
        df     = pd.DataFrame({"amount": values})
        result = calculate_totals(df, ["amount"])
        assert result["amount"] == pytest.approx(expected_total, rel=1e-6)


# ============================================================
# TESTS — Integration (Read → Clean → Total)
# ============================================================

class TestFullPipeline:
    """End-to-end tests simulating a real data processing pipeline."""

    def test_full_pipeline_csv_to_totals(self, dirty_df, tmp_path):
        """
        Simulate a real pipeline:
          1. Write dirty data to CSV
          2. Read it back
          3. Clean nulls (fill strategy)
          4. Calculate totals
        """
        csv_file = tmp_path / "pipeline.csv"
        dirty_df.to_csv(csv_file, index=False)

        df       = read_data(str(csv_file))
        cleaned  = clean_nulls(df, strategy="fill", fill_value=0)
        result   = calculate_totals(cleaned, ["sales", "expenses"])

        assert "sales"    in result
        assert "expenses" in result
        assert result["sales"]    >= 0
        assert result["expenses"] >= 0

    def test_pipeline_preserves_clean_data(self, sample_df, tmp_path):
        """Clean data should be unchanged through the full pipeline."""
        csv_file = tmp_path / "clean.csv"
        sample_df.to_csv(csv_file, index=False)

        df      = read_data(str(csv_file))
        cleaned = clean_nulls(df, strategy="drop")
        result  = calculate_totals(cleaned, ["sales", "expenses", "units"])

        assert result["sales"]    == pytest.approx(sample_df["sales"].sum(),    rel=1e-5)
        assert result["expenses"] == pytest.approx(sample_df["expenses"].sum(), rel=1e-5)
        assert result["units"]    == pytest.approx(sample_df["units"].sum(),    rel=1e-5)

    def test_pipeline_multiple_clean_strategies_produce_valid_totals(self, dirty_df, tmp_path):
        """All cleaning strategies should lead to valid (non-null) totals."""
        csv_file = tmp_path / "multi.csv"
        dirty_df.to_csv(csv_file, index=False)
        df = read_data(str(csv_file))

        for strategy in ("drop", "fill", "mean"):
            cleaned = clean_nulls(df, strategy=strategy, fill_value=0)
            result  = calculate_totals(cleaned, ["sales", "expenses"])
            assert result["sales"]    is not None
            assert result["expenses"] is not None