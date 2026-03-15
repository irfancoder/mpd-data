"""Tests for data pipeline."""

import pytest
import pandas as pd
import os
from src.data_loader import (
    parse_price,
    parse_date,
    clean_numeric_area,
    load_and_clean_data,
)
from src.config import OUTPUT_DIR


def test_parse_price():
    assert parse_price("RM470,000.00") == 470000.0
    assert parse_price("RM 1,234,567.89") == 1234567.89
    assert pd.isna(parse_price(None))
    assert pd.isna(parse_price("invalid"))


def test_parse_date():
    result = parse_date("March 2024")
    assert result.year == 2024
    assert result.month == 3
    assert pd.isna(parse_date("invalid"))


def test_clean_numeric_area():
    assert clean_numeric_area("374.00") == 374.0
    assert clean_numeric_area(374.0) == 374.0
    assert pd.isna(clean_numeric_area("invalid"))


def test_load_and_clean_data():
    """Integration test for full data loading."""
    df = load_and_clean_data()

    # Check basic structure
    assert len(df) > 400000
    assert "state" in df.columns
    assert "price_rm" in df.columns
    assert "price_per_sqft" in df.columns

    # Check data quality
    assert df["price_rm"].notna().sum() > 400000
    assert df["state"].notna().sum() > 390000


def test_all_views_generated():
    """Test that all expected Parquet files are created."""
    expected_views = [
        "transactions_clean",
        "districts_summary",
        "schemes_summary",
        "timeline_rolling_12m_state",
        "timeline_rolling_12m_district",
        "timeline_rolling_12m_scheme",
        "price_trends_monthly",
        "affordability_matrix",
        "property_type_comparison",
        "tenure_analysis",
        "hot_areas",
        "spatial_index",
        "outliers_flagged",
    ]

    for view in expected_views:
        filepath = os.path.join(OUTPUT_DIR, f"{view}.parquet")
        assert os.path.exists(filepath), f"Missing view: {view}"
        assert os.path.getsize(filepath) > 0, f"Empty view: {view}"


def test_views_readable():
    """Test that all views can be read back."""
    views = [
        "districts_summary",
        "schemes_summary",
        "timeline_rolling_12m_state",
        "timeline_rolling_12m_district",
    ]

    for view in views:
        filepath = os.path.join(OUTPUT_DIR, f"{view}.parquet")
        df = pd.read_parquet(filepath)
        assert len(df) > 0, f"Empty dataframe: {view}"
        assert len(df.columns) > 0, f"No columns: {view}"


def test_timeline_views_structure():
    """Test timeline views have correct structure."""
    # Test state timeline
    df = pd.read_parquet(os.path.join(OUTPUT_DIR, "timeline_rolling_12m_state.parquet"))
    assert "state" in df.columns
    assert "date" in df.columns
    assert "rolling_12m_median_price" in df.columns
    assert "yoy_change_pct" in df.columns

    # Test district timeline
    df = pd.read_parquet(
        os.path.join(OUTPUT_DIR, "timeline_rolling_12m_district.parquet")
    )
    assert "district" in df.columns

    # Test scheme timeline
    df = pd.read_parquet(
        os.path.join(OUTPUT_DIR, "timeline_rolling_12m_scheme.parquet")
    )
    assert "scheme_name" in df.columns


def test_schemes_summary_has_required_columns():
    """Test schemes summary has all expected columns."""
    df = pd.read_parquet(os.path.join(OUTPUT_DIR, "schemes_summary.parquet"))

    required_cols = [
        "state",
        "district",
        "mukim",
        "scheme_name",
        "median_price",
        "price_25th",
        "price_75th",
        "total_transactions",
        "price_volatility",
    ]

    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"


def test_affordability_matrix_percentiles():
    """Test affordability matrix has all percentiles."""
    df = pd.read_parquet(os.path.join(OUTPUT_DIR, "affordability_matrix.parquet"))

    percentile_cols = ["price_p10", "price_p25", "price_p50", "price_p75", "price_p90"]

    for col in percentile_cols:
        assert col in df.columns, f"Missing column: {col}"


def test_data_quality_scores():
    """Test timeline views have data quality scores."""
    df = pd.read_parquet(
        os.path.join(OUTPUT_DIR, "timeline_rolling_12m_district.parquet")
    )

    assert "data_quality_score" in df.columns
    valid_scores = ["A", "B", "C", "D"]
    actual_scores = df["data_quality_score"].dropna().unique()

    for score in actual_scores:
        assert score in valid_scores, f"Invalid score: {score}"
