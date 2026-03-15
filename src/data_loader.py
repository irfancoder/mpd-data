"""Data loading and initial cleaning functions."""

import pandas as pd
import numpy as np
from typing import Tuple
from src.config import INPUT_FILE, DISTRICT_TO_STATE


def load_raw_data(file_path: str = None) -> pd.DataFrame:
    """Load raw CSV data with proper encoding and types."""
    if file_path is None:
        file_path = INPUT_FILE

    df = pd.read_csv(file_path, sep="\t", encoding="utf-16", low_memory=False)
    return df


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names."""
    column_mapping = {
        "Property Type": "property_type",
        "District": "district",
        "Mukim": "mukim",
        "Scheme Name/Area": "scheme_name",
        "Road Name": "road_name",
        "Month, Year of Transaction Date": "transaction_date_raw",
        "Tenure": "tenure",
        "Land/Parcel Area": "land_area",
        "Unit": "land_area_unit",
        "Main Floor Area": "floor_area",
        "Unit         ": "floor_area_unit",  # Note: extra spaces in original
        "Unit Level": "unit_level",
        "Transaction Price  ": "price_raw",  # Note: extra spaces
    }

    df = df.rename(columns=column_mapping)

    # Drop unnamed column if exists
    unnamed_cols = [col for col in df.columns if "Unnamed" in col]
    df = df.drop(columns=unnamed_cols, errors="ignore")

    return df


def parse_price(price_str: str) -> float:
    """Parse price string like 'RM470,000.00' to float."""
    if pd.isna(price_str):
        return np.nan

    # Remove RM prefix and commas
    cleaned = str(price_str).replace("RM", "").replace(",", "").strip()

    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def parse_date(date_str: str) -> pd.Timestamp:
    """Parse date string like 'March 2024' to datetime."""
    if pd.isna(date_str):
        return pd.NaT

    try:
        return pd.to_datetime(date_str, format="%B %Y")
    except ValueError:
        return pd.NaT


def clean_numeric_area(value) -> float:
    """Clean and convert area values to numeric."""
    if pd.isna(value):
        return np.nan

    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan


def normalize_district_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize district names to match GeoJSON format."""
    # Mapping from dataset names to GeoJSON names
    DISTRICT_NAME_MAPPING = {
        # Sarawak: Remove "Bahagian " prefix
        "Bahagian Betong": "Betong",
        "Bahagian Bintulu": "Bintulu",
        "Bahagian Kapit": "Kapit",
        "Bahagian Kuching": "Kuching",
        "Bahagian Limbang": "Limbang",
        "Bahagian Miri": "Miri",
        "Bahagian Mukah": "Mukah",
        "Bahagian Samarahan": "Samarahan",
        "Bahagian Sarikei": "Sarikei",
        "Bahagian Sarikie": "Sarikei",  # Typo fix
        "Bahagian Serian": "Serian",
        "Bahagian Sibu": "Sibu",
        "Bahagian Sri Aman": "Sri Aman",
        # Other spelling normalizations
        "Kota Bahru": "Kota Bharu",
        "Bandar Baru": "Bandar Baharu",
        # Small district mapped to parent district
        "DAERAH KECIL MUADZAM SHAH": "Rompin",  # Sub-district within Rompin
        # Old district name replaced by new district
        "Labuk Sugut": "Beluran",  # Labuk Sugut is old name, now part of Beluran
    }

    # Apply mapping
    df["district_original"] = df["district"].copy()  # Keep original for reference
    df["district"] = df["district"].replace(DISTRICT_NAME_MAPPING)

    # Log transformations
    mask = df["district"] != df["district_original"]
    transformed = df.loc[mask, "district_original"].unique()
    if len(transformed) > 0:
        print(f"Normalized {len(transformed)} district names:")
        for orig in transformed:
            new = DISTRICT_NAME_MAPPING.get(orig, orig)
            print(f"  - {orig} → {new}")

    return df


def add_state_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add state column based on district mapping."""
    df["state"] = df["district"].map(DISTRICT_TO_STATE)

    # Log unmapped districts
    unmapped = df[df["state"].isna()]["district"].unique()
    if len(unmapped) > 0:
        print(f"Warning: {len(unmapped)} unmapped districts: {unmapped}")

    return df


def calculate_price_per_sqft(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate price per sqft using floor area (preferred) or land area."""
    # Convert sqm to sqft (1 sqm = 10.764 sqft)
    SQFT_PER_SQM = 10.764

    # Calculate price per sqft
    conditions = [
        (df["floor_area"].notna()) & (df["floor_area"] > 0),
        (df["land_area"].notna()) & (df["land_area"] > 0),
    ]

    choices = [
        df["price_rm"] / (df["floor_area"] * SQFT_PER_SQM),
        df["price_rm"] / (df["land_area"] * SQFT_PER_SQM),
    ]

    df["price_per_sqft"] = np.select(conditions, choices, default=np.nan)
    df["price_per_sqm"] = df["price_rm"] / df[["floor_area", "land_area"]].max(axis=1)

    return df


def flag_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Flag price and area outliers."""
    from src.config import PRICE_OUTLIER_HIGH_THRESHOLD, PRICE_OUTLIER_LOW_THRESHOLD

    df["outlier_flag"] = None

    # Price outliers
    df.loc[df["price_rm"] > PRICE_OUTLIER_HIGH_THRESHOLD, "outlier_flag"] = (
        "extreme_high_price"
    )
    df.loc[df["price_rm"] < PRICE_OUTLIER_LOW_THRESHOLD, "outlier_flag"] = (
        "extreme_low_price"
    )

    # Area outliers (reasonable ranges for Malaysia)
    df.loc[df["price_per_sqft"] > 5000, "outlier_flag"] = "extreme_price_per_sqft"
    df.loc[df["price_per_sqft"] < 100, "outlier_flag"] = "extreme_low_price_per_sqft"

    return df


def load_and_clean_data(file_path: str = INPUT_FILE) -> pd.DataFrame:
    """Main function to load and clean all data."""
    print("Loading raw data...")
    df = load_raw_data(file_path)
    print(f"Loaded {len(df):,} records")

    print("Cleaning column names...")
    df = clean_column_names(df)

    print("Normalizing district names...")
    df = normalize_district_names(df)

    print("Parsing prices...")
    df["price_rm"] = df["price_raw"].apply(parse_price)

    print("Parsing dates...")
    df["transaction_date"] = df["transaction_date_raw"].apply(parse_date)
    df["year"] = df["transaction_date"].dt.year
    df["month"] = df["transaction_date"].dt.month
    df["year_month"] = df["transaction_date"].dt.to_period("M")

    print("Cleaning area data...")
    df["land_area"] = df["land_area"].apply(clean_numeric_area)
    df["floor_area"] = df["floor_area"].apply(clean_numeric_area)

    print("Adding state mapping...")
    df = add_state_column(df)

    print("Calculating price per sqft...")
    df = calculate_price_per_sqft(df)

    print("Flagging outliers...")
    df = flag_outliers(df)

    # Add unique transaction ID
    df["transaction_id"] = range(len(df))

    print(f"\nCleaning complete:")
    print(f"  - Records with valid prices: {df['price_rm'].notna().sum():,}")
    print(f"  - Records with dates: {df['transaction_date'].notna().sum():,}")
    print(f"  - Records with states: {df['state'].notna().sum():,}")
    print(f"  - Records with price per sqft: {df['price_per_sqft'].notna().sum():,}")

    return df
