"""Aggregation functions for timeline and trend views."""

import pandas as pd
import numpy as np
from typing import List, Tuple


def calculate_rolling_12m_metrics(
    df: pd.DataFrame,
    group_cols: List[str],
    date_col: str = "transaction_date",
    value_col: str = "price_rm",
) -> pd.DataFrame:
    """Calculate rolling 12-month metrics for timeline views."""

    # Create monthly date range
    df = df.copy()
    df["year_month"] = df[date_col].dt.to_period("M")

    # Calculate monthly aggregations first
    monthly = (
        df.groupby(group_cols + ["year_month"])
        .agg({value_col: ["median", "count"], "price_per_sqft": "median"})
        .reset_index()
    )

    # Flatten column names
    monthly.columns = group_cols + [
        "year_month",
        "median_price",
        "transaction_count",
        "median_price_per_sqft",
    ]

    # Generate all months in range
    all_months = pd.period_range(
        start=df["year_month"].min(), end=df["year_month"].max(), freq="M"
    )

    # Create complete time series for each group using merge instead of reindex
    all_groups = df[group_cols].drop_duplicates().reset_index(drop=True)

    # Create cartesian product of groups and months
    all_combinations = []
    for _, group_row in all_groups.iterrows():
        for month in all_months:
            row_dict = {col: group_row[col] for col in group_cols}
            row_dict["year_month"] = month
            all_combinations.append(row_dict)

    complete_index = pd.DataFrame(all_combinations)

    # Merge with actual data
    result = complete_index.merge(monthly, on=group_cols + ["year_month"], how="left")

    # Sort by group and date for rolling calculations
    result = result.sort_values(group_cols + ["year_month"])

    # Calculate rolling 12-month metrics
    def rolling_12m_median(x):
        """Calculate median of last 12 non-null values."""
        return x.rolling(window=12, min_periods=6).median()

    def rolling_12m_count(x):
        """Calculate sum of last 12 months."""
        return x.rolling(window=12, min_periods=6).sum()

    # Apply rolling calculations per group
    result["rolling_12m_median_price"] = result.groupby(group_cols)[
        "median_price"
    ].transform(rolling_12m_median)
    result["rolling_12m_transaction_count"] = result.groupby(group_cols)[
        "transaction_count"
    ].transform(rolling_12m_count)
    result["rolling_12m_median_price_per_sqft"] = result.groupby(group_cols)[
        "median_price_per_sqft"
    ].transform(rolling_12m_median)

    # Calculate YoY change (compare current 12m vs 12m from 1 year ago)
    def yoy_change(x):
        """Calculate year-over-year percentage change."""
        return ((x - x.shift(12)) / x.shift(12) * 100).round(2)

    result["yoy_change_pct"] = result.groupby(group_cols)[
        "rolling_12m_median_price"
    ].transform(yoy_change)

    # Calculate MoM change
    def mom_change(x):
        """Calculate month-over-month percentage change."""
        return ((x - x.shift(1)) / x.shift(1) * 100).round(2)

    result["mom_change_pct"] = result.groupby(group_cols)[
        "rolling_12m_median_price"
    ].transform(mom_change)

    # Add data quality score based on sample size
    def quality_score(count):
        if pd.isna(count) or count < 20:
            return "D"
        elif count < 50:
            return "C"
        elif count < 100:
            return "B"
        else:
            return "A"

    result["data_quality_score"] = result["rolling_12m_transaction_count"].apply(
        quality_score
    )

    # Convert period to timestamp
    result["date"] = result["year_month"].dt.to_timestamp()

    return result


def create_timeline_state_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 11: State-level rolling 12-month timeline."""

    df_clean = df[df["outlier_flag"].isna()].copy()

    timeline = calculate_rolling_12m_metrics(
        df_clean,
        group_cols=["state"],
        date_col="transaction_date",
        value_col="price_rm",
    )

    # Select and rename columns
    columns = [
        "state",
        "date",
        "rolling_12m_median_price",
        "rolling_12m_median_price_per_sqft",
        "rolling_12m_transaction_count",
        "yoy_change_pct",
        "mom_change_pct",
        "data_quality_score",
    ]

    return timeline[columns]


def create_timeline_district_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 12: District-level rolling 12-month timeline."""

    df_clean = df[df["outlier_flag"].isna()].copy()

    timeline = calculate_rolling_12m_metrics(
        df_clean,
        group_cols=["state", "district"],
        date_col="transaction_date",
        value_col="price_rm",
    )

    columns = [
        "state",
        "district",
        "date",
        "rolling_12m_median_price",
        "rolling_12m_median_price_per_sqft",
        "rolling_12m_transaction_count",
        "yoy_change_pct",
        "mom_change_pct",
        "data_quality_score",
    ]

    return timeline[columns]


def create_timeline_scheme_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 13: Scheme-level rolling 12-month timeline."""
    # No minimum threshold - include all schemes as requested

    df_clean = df[df["outlier_flag"].isna()].copy()

    timeline = calculate_rolling_12m_metrics(
        df_clean,
        group_cols=["state", "district", "mukim", "scheme_name"],
        date_col="transaction_date",
        value_col="price_rm",
    )

    columns = [
        "state",
        "district",
        "mukim",
        "scheme_name",
        "date",
        "rolling_12m_median_price",
        "rolling_12m_median_price_per_sqft",
        "rolling_12m_transaction_count",
        "yoy_change_pct",
        "mom_change_pct",
        "data_quality_score",
    ]

    return timeline[columns]


def create_price_trends_monthly_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 4: Monthly price trends by district and property type."""

    df_clean = df[df["outlier_flag"].isna()].copy()
    df_clean["year_month"] = df_clean["transaction_date"].dt.to_period("M")

    trends = (
        df_clean.groupby(["state", "district", "property_type", "year_month"])
        .agg(
            {
                "price_rm": "median",
                "price_per_sqft": "median",
                "transaction_id": "count",
                "floor_area": "mean",
                "land_area": "mean",
            }
        )
        .reset_index()
    )

    trends.columns = [
        "state",
        "district",
        "property_type",
        "year_month",
        "median_price",
        "median_price_per_sqft",
        "transaction_count",
        "avg_floor_area",
        "avg_land_area",
    ]

    trends["date"] = trends["year_month"].dt.to_timestamp()

    return trends


def create_hot_areas_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 8: Hot areas ranked by activity and growth."""

    df_clean = df[df["outlier_flag"].isna()].copy()

    # Calculate metrics for each scheme
    from src.config import MIN_TRANSACTIONS_FOR_SCHEME_SUMMARY

    scheme_stats = (
        df_clean.groupby(["state", "district", "scheme_name"])
        .agg(
            {
                "transaction_id": "count",
                "price_rm": "median",
                "transaction_date": ["min", "max"],
            }
        )
        .reset_index()
    )

    scheme_stats.columns = [
        "state",
        "district",
        "scheme_name",
        "total_transactions",
        "median_price",
        "first_transaction",
        "last_transaction",
    ]

    # Filter schemes with sufficient data
    scheme_stats = scheme_stats[
        scheme_stats["total_transactions"] >= MIN_TRANSACTIONS_FOR_SCHEME_SUMMARY
    ]

    # Calculate activity score (transactions per month)
    scheme_stats["months_active"] = (
        (scheme_stats["last_transaction"] - scheme_stats["first_transaction"]).dt.days
        / 30.44
    ).clip(lower=1)  # At least 1 month
    scheme_stats["activity_score"] = (
        scheme_stats["total_transactions"] / scheme_stats["months_active"]
    ).round(2)

    # Calculate price growth (compare recent 6 months vs previous 6 months)
    df_clean["year_month"] = df_clean["transaction_date"].dt.to_period("M")
    latest_date = df_clean["transaction_date"].max()

    recent_period = df_clean[
        df_clean["transaction_date"] >= latest_date - pd.DateOffset(months=6)
    ]
    previous_period = df_clean[
        (df_clean["transaction_date"] < latest_date - pd.DateOffset(months=6))
        & (df_clean["transaction_date"] >= latest_date - pd.DateOffset(months=12))
    ]

    recent_medians = recent_period.groupby(["state", "district", "scheme_name"])[
        "price_rm"
    ].median()
    previous_medians = previous_period.groupby(["state", "district", "scheme_name"])[
        "price_rm"
    ].median()

    growth = (
        (recent_medians - previous_medians) / previous_medians * 100
    ).reset_index()
    growth.columns = ["state", "district", "scheme_name", "price_growth_6m_pct"]

    scheme_stats = scheme_stats.merge(
        growth, on=["state", "district", "scheme_name"], how="left"
    )

    # Calculate 1-year growth
    one_year_ago = latest_date - pd.DateOffset(years=1)
    year_ago_period = df_clean[df_clean["transaction_date"] <= one_year_ago]

    if len(year_ago_period) > 0:
        year_ago_medians = year_ago_period.groupby(
            ["state", "district", "scheme_name"]
        )["price_rm"].median()
        yoy_growth = (
            (recent_medians - year_ago_medians) / year_ago_medians * 100
        ).reset_index()
        yoy_growth.columns = [
            "state",
            "district",
            "scheme_name",
            "price_growth_1yr_pct",
        ]
        scheme_stats = scheme_stats.merge(
            yoy_growth, on=["state", "district", "scheme_name"], how="left"
        )
    else:
        scheme_stats["price_growth_1yr_pct"] = np.nan

    # Calculate market hotness rank (composite score)
    scheme_stats["hotness_score"] = (
        scheme_stats["activity_score"] * 0.4
        + scheme_stats["price_growth_6m_pct"].fillna(0) * 0.3
        + scheme_stats["total_transactions"]
        / scheme_stats["total_transactions"].max()
        * 100
        * 0.3
    ).round(2)

    scheme_stats["market_hotness_rank"] = (
        scheme_stats["hotness_score"].rank(ascending=False, method="min").astype(int)
    )

    return scheme_stats
