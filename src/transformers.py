"""Data transformation functions for creating views."""

import pandas as pd
import numpy as np
from typing import Dict, List


def create_transactions_clean_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 1: Clean transactions with all fields."""
    columns = [
        "transaction_id",
        "property_type",
        "state",
        "district",
        "mukim",
        "scheme_name",
        "transaction_date",
        "year",
        "month",
        "tenure",
        "price_rm",
        "land_area",
        "floor_area",
        "price_per_sqm",
        "price_per_sqft",
        "outlier_flag",
    ]

    view = df[columns].copy()
    return view


def create_districts_summary_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 2: District-level aggregated metrics."""

    # Filter out extreme outliers for summary stats
    df_clean = df[df["outlier_flag"].isna()].copy()

    summary = (
        df_clean.groupby(["state", "district"])
        .agg(
            {
                "transaction_id": "count",
                "price_rm": [
                    "median",
                    lambda x: x.quantile(0.25),
                    lambda x: x.quantile(0.75),
                    "min",
                    "max",
                ],
                "price_per_sqft": [
                    "median",
                    lambda x: x.quantile(0.25),
                    lambda x: x.quantile(0.75),
                ],
                "floor_area": "median",
                "land_area": "median",
            }
        )
        .reset_index()
    )

    # Flatten column names
    summary.columns = [
        "state",
        "district",
        "total_transactions",
        "median_price",
        "price_25th",
        "price_75th",
        "min_price",
        "max_price",
        "median_price_per_sqft",
        "price_per_sqft_25th",
        "price_per_sqft_75th",
        "median_floor_area",
        "median_land_area",
    ]

    # Add property type breakdown as JSON string
    type_breakdown = (
        df_clean.groupby(["state", "district", "property_type"])
        .size()
        .unstack(fill_value=0)
    )
    type_breakdown_dict = type_breakdown.apply(lambda x: x.to_dict(), axis=1)
    summary["property_type_breakdown"] = summary.apply(
        lambda row: type_breakdown_dict.get((row["state"], row["district"]), {}), axis=1
    )

    return summary


def create_schemes_summary_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 3: Scheme-level aggregated metrics."""
    from src.config import MIN_TRANSACTIONS_FOR_SCHEME_SUMMARY

    # Filter out extreme outliers
    df_clean = df[df["outlier_flag"].isna()].copy()

    # Only include schemes with sufficient data
    scheme_counts = df_clean.groupby(["state", "district", "scheme_name"]).size()
    valid_schemes = scheme_counts[
        scheme_counts >= MIN_TRANSACTIONS_FOR_SCHEME_SUMMARY
    ].index

    df_filtered = (
        df_clean.set_index(["state", "district", "scheme_name"])
        .loc[valid_schemes]
        .reset_index()
    )

    summary = (
        df_filtered.groupby(["state", "district", "mukim", "scheme_name"])
        .agg(
            {
                "transaction_id": "count",
                "price_rm": [
                    "median",
                    lambda x: x.quantile(0.25),
                    lambda x: x.quantile(0.75),
                ],
                "price_per_sqft": [
                    "median",
                    lambda x: x.quantile(0.25),
                    lambda x: x.quantile(0.75),
                ],
                "transaction_date": ["min", "max"],
            }
        )
        .reset_index()
    )

    summary.columns = [
        "state",
        "district",
        "mukim",
        "scheme_name",
        "total_transactions",
        "median_price",
        "price_25th",
        "price_75th",
        "median_price_per_sqft",
        "price_per_sqft_25th",
        "price_per_sqft_75th",
        "first_transaction_date",
        "last_transaction_date",
    ]

    # Calculate price volatility (coefficient of variation)
    volatility = (
        df_filtered.groupby(["state", "district", "scheme_name"])["price_rm"]
        .agg(lambda x: x.std() / x.mean())
        .reset_index()
    )
    volatility.columns = ["state", "district", "scheme_name", "price_volatility"]
    summary = summary.merge(volatility, on=["state", "district", "scheme_name"])

    # Add tenure breakdown
    tenure_breakdown = (
        df_filtered.groupby(["state", "district", "scheme_name", "tenure"])
        .size()
        .unstack(fill_value=0)
    )
    tenure_dict = tenure_breakdown.apply(lambda x: x.to_dict(), axis=1)
    summary["tenure_breakdown"] = summary.apply(
        lambda row: tenure_dict.get(
            (row["state"], row["district"], row["scheme_name"]), {}
        ),
        axis=1,
    )

    return summary


def create_affordability_matrix_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 5: Affordability percentiles by district and property type."""

    df_clean = df[df["outlier_flag"].isna()].copy()

    percentiles = [10, 25, 50, 75, 90]

    summary = (
        df_clean.groupby(["state", "district", "property_type"])
        .agg(
            {
                "price_rm": [
                    (f"price_p{p}", lambda x: x.quantile(p / 100)) for p in percentiles
                ],
                "price_per_sqft": [
                    (f"sqft_p{p}", lambda x: x.quantile(p / 100)) for p in percentiles
                ],
                "floor_area": [
                    (f"area_p{p}", lambda x: x.quantile(p / 100)) for p in percentiles
                ],
                "transaction_id": "count",
            }
        )
        .reset_index()
    )

    # Flatten columns
    summary.columns = (
        ["state", "district", "property_type"]
        + [f"price_p{p}" for p in percentiles]
        + [f"sqft_p{p}" for p in percentiles]
        + [f"area_p{p}" for p in percentiles]
        + ["total_transactions"]
    )

    return summary


def create_property_type_comparison_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 6: Cross-property-type comparison by district."""

    df_clean = df[df["outlier_flag"].isna()].copy()

    summary = (
        df_clean.groupby(["state", "district", "property_type"])
        .agg(
            {
                "price_rm": "median",
                "price_per_sqft": "median",
                "transaction_id": "count",
            }
        )
        .reset_index()
    )

    summary.columns = [
        "state",
        "district",
        "property_type",
        "median_price",
        "median_price_per_sqft",
        "transaction_count",
    ]

    # Calculate market share within district
    district_totals = (
        summary.groupby(["state", "district"])["transaction_count"].sum().reset_index()
    )
    district_totals.columns = ["state", "district", "district_total"]

    summary = summary.merge(district_totals, on=["state", "district"])
    summary["market_share_pct"] = (
        summary["transaction_count"] / summary["district_total"] * 100
    ).round(2)

    # Calculate premium vs cheapest type in district
    cheapest_by_district = (
        summary.groupby(["state", "district"])["median_price"].min().reset_index()
    )
    cheapest_by_district.columns = ["state", "district", "cheapest_price"]

    summary = summary.merge(cheapest_by_district, on=["state", "district"])
    summary["premium_vs_cheapest_pct"] = (
        (summary["median_price"] - summary["cheapest_price"])
        / summary["cheapest_price"]
        * 100
    ).round(2)

    return summary


def create_tenure_analysis_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 7: Freehold vs Leasehold analysis."""

    df_clean = df[df["outlier_flag"].isna()].copy()

    # Filter to only Freehold and Leasehold
    df_tenure = df_clean[df_clean["tenure"].isin(["Freehold", "Leasehold"])].copy()

    summary = (
        df_tenure.groupby(["state", "district", "property_type", "tenure"])
        .agg(
            {
                "price_rm": "median",
                "price_per_sqft": "median",
                "transaction_id": "count",
            }
        )
        .reset_index()
    )

    # Pivot to compare freehold vs leasehold
    pivoted = summary.pivot_table(
        index=["state", "district", "property_type"],
        columns="tenure",
        values=["price_rm", "price_per_sqft", "transaction_id"],
        fill_value=np.nan,
    ).reset_index()

    # Flatten column names
    pivoted.columns = [
        " ".join(col).strip() if col[1] else col[0] for col in pivoted.columns.values
    ]
    pivoted = pivoted.rename(
        columns={
            "price_rm Freehold": "freehold_median_price",
            "price_rm Leasehold": "leasehold_median_price",
            "price_per_sqft Freehold": "freehold_median_price_per_sqft",
            "price_per_sqft Leasehold": "leasehold_median_price_per_sqft",
            "transaction_id Freehold": "sample_size_freehold",
            "transaction_id Leasehold": "sample_size_leasehold",
        }
    )

    # Calculate premium
    pivoted["freehold_premium_pct"] = (
        (pivoted["freehold_median_price"] - pivoted["leasehold_median_price"])
        / pivoted["leasehold_median_price"]
        * 100
    ).round(2)

    return pivoted


def create_spatial_index_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 9: Geographic hierarchy lookup."""
    from src.config import MIN_TRANSACTIONS_FOR_SCHEME_SUMMARY

    summary = (
        df.groupby(["state", "district", "mukim", "scheme_name"])
        .agg({"transaction_id": "count", "transaction_date": ["min", "max"]})
        .reset_index()
    )

    summary.columns = [
        "state",
        "district",
        "mukim",
        "scheme_name",
        "transaction_count",
        "first_transaction",
        "last_transaction",
    ]

    summary["has_sufficient_data"] = (
        summary["transaction_count"] >= MIN_TRANSACTIONS_FOR_SCHEME_SUMMARY
    )

    return summary


def create_outliers_flagged_view(df: pd.DataFrame) -> pd.DataFrame:
    """View 10: Flagged outlier transactions."""

    outliers = df[df["outlier_flag"].notna()].copy()

    columns = [
        "transaction_id",
        "state",
        "district",
        "scheme_name",
        "property_type",
        "price_rm",
        "price_per_sqft",
        "floor_area",
        "land_area",
        "outlier_flag",
        "transaction_date",
    ]

    return outliers[columns]
