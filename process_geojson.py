#!/usr/bin/env python3
"""
GeoJSON Processing Script

This script:
1. Fixes district name mappings in GeoJSON files
2. Creates individual GeoJSON files for each state and district
3. Outputs to output/geojson/ directory

Usage:
    python3 process_geojson.py
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Mapping from GeoJSON names to standardized dataset names
# Key: GeoJSON name, Value: Dataset name (or None to exclude)
DISTRICT_MAPPING = {
    # Spelling corrections (fixing GeoJSON mistakes)
    "Ulu Langat": "Hulu Langat",
    "Ulu Selangor": "Hulu Selangor",
    # Name standardizations
    "Cameron Highlands": "Cameron Highland",
    "W.P. Kuala Lumpur": "Kuala Lumpur",
    "W.P. Labuan": "Labuan",
    "W.P. Putrajaya": "Putrajaya",
    # Perak - spelling variation (GeoJSON has "Larut Dan Matang", dataset has "Larut Matang")
    "Larut Dan Matang": "Larut Matang",
    # Sabah districts - all included
    "Kota Belud": "Kota Belud",
    "Kota Marudu": "Kota Marudu",
    "Kudat": "Kudat",
    "Kunak": "Kunak",
    "Lahad Datu": "Lahad Datu",
    "Papar": "Papar",
    "Penampang": "Penampang",
    "Pitas": "Pitas",
    "Putatan": "Putatan",
    "Ranau": "Ranau",
    "Semporna": "Semporna",
    "Sipitang": "Sipitang",
    "Tambunan": "Tambunan",
    "Tawau": "Tawau",
    "Tenom": "Tenom",
    "Tuaran": "Tuaran",
    "Beluran": "Beluran",
    # Sarawak districts - use individual names (remove "Bahagian" concept)
    "Betong": "Betong",
    "Bintulu": "Bintulu",
    "Kapit": "Kapit",
    "Kuching": "Kuching",
    "Limbang": "Limbang",
    "Miri": "Miri",
    "Mukah": "Mukah",
    "Samarahan": "Samarahan",
    "Sarikei": "Sarikei",
    "Serian": "Serian",
    "Sibu": "Sibu",
    "Sri Aman": "Sri Aman",
    # Districts to exclude (not in dataset)
    "Asajaya": None,
    "Belaga": None,
    "Beluru": None,
    "Bukit Mabong": None,
    "Dalat": None,
    "Daro": None,
    "Julau": None,
    "Kabong": None,
    "Kalabakan": None,
    "Kanowit": None,
    "Kecil Lojing": None,
    "Lawas": None,
    "Lubok Antu": None,
    "Lundu": None,
    "Marudi": None,
    "Matu": None,
    "Meradong": None,
    "Pakan": None,
    "Pusa": None,
    "Saratok": None,
    "Selangau": None,
    "Sebauh": None,
    "Subis": None,
    "Tatau": None,
    "Telang Usan": None,
    "Tanjung Manis": None,
    "Tebedu": None,
    "Maradong": None,
    "Simunjan": None,
    "Song": None,
    "Bau": None,
    "Kuala Penyu": None,
    "Kinabatangan": None,
    "Nabawan": None,
    "Telupid": None,
    "Tongod": None,
    "Labuk Sugut": None,  # Old name, now part of Beluran
}

# State name mapping (GeoJSON -> standardized)
STATE_MAPPING = {
    "Kedah": "Kedah",
    "Kelantan": "Kelantan",
    "Perak": "Perak",
    "Pulau Pinang": "Penang",
    "WP K Lumpur": "Kuala Lumpur",
    "Negeri Sembilan": "Negeri Sembilan",
    "Melaka": "Melaka",
    "Perlis": "Perlis",
    "Pahang": "Pahang",
    "Terengganu": "Terengganu",
    "WP Putrajaya": "Putrajaya",
    "WP Labuan": "Labuan",
    "Selangor": "Selangor",
    "Sabah": "Sabah",
    "Johor": "Johor",
    "Sarawak": "Sarawak",
}

# State code to name mapping
STATE_CODE_TO_NAME = {
    "KDH": "Kedah",
    "KTN": "Kelantan",
    "PRK": "Perak",
    "PNG": "Penang",
    "KUL": "Kuala Lumpur",
    "NSN": "Negeri Sembilan",
    "MLK": "Melaka",
    "PLS": "Perlis",
    "PHG": "Pahang",
    "TRG": "Terengganu",
    "PJY": "Putrajaya",
    "LBN": "Labuan",
    "SGR": "Selangor",
    "SBH": "Sabah",
    "JHR": "Johor",
    "SWK": "Sarawak",
}

# Reverse mapping for Sarawak: individual district -> "Bahagian X"
SARAWAK_REVERSE_MAPPING = {
    "Betong": "Bahagian Betong",
    "Bintulu": "Bahagian Bintulu",
    "Kapit": "Bahagian Kapit",
    "Kuching": "Bahagian Kuching",
    "Limbang": "Bahagian Limbang",
    "Miri": "Bahagian Miri",
    "Mukah": "Bahagian Mukah",
    "Samarahan": "Bahagian Samarahan",
    "Sarikei": "Bahagian Sarikei",
    "Serian": "Bahagian Serian",
    "Sibu": "Bahagian Sibu",
    "Sri Aman": "Bahagian Sri Aman",
}


def kebab_case(name):
    """Convert name to kebab-case for filenames."""
    return (
        name.lower()
        .replace(" ", "-")
        .replace(".", "")
        .replace("(", "")
        .replace(")", "")
    )


def load_dataset_districts():
    """Load unique districts from the dataset with normalization."""
    df = pd.read_csv(
        "src/raw/Open Transaction Data_Residential.csv", sep="\t", encoding="utf-16"
    )

    # Apply same normalization as data_loader.py
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
        "Bahagian Sarikie": "Sarikei",
        "Bahagian Serian": "Serian",
        "Bahagian Sibu": "Sibu",
        "Bahagian Sri Aman": "Sri Aman",
        # Other spelling normalizations
        "Kota Bahru": "Kota Bharu",
        "Bandar Baru": "Bandar Baharu",
        # Small district mapped to parent district
        "DAERAH KECIL MUADZAM SHAH": "Rompin",
        # Old district name replaced by new district
        "Labuk Sugut": "Beluran",  # Labuk Sugut is old name, now part of Beluran
    }

    df["District"] = df["District"].replace(DISTRICT_NAME_MAPPING)
    return set(df["District"].unique())


def is_in_dataset(district_name, dataset_districts):
    """Check if district is in dataset, handling Sarawak "Bahagian" format."""
    # Direct match
    if district_name in dataset_districts:
        return True

    # Check if it's a Sarawak district with "Bahagian" prefix
    if district_name in SARAWAK_REVERSE_MAPPING:
        bahagian_name = SARAWAK_REVERSE_MAPPING[district_name]
        if bahagian_name in dataset_districts:
            return True

    return False


def process_district_geojson():
    """Process district GeoJSON and create individual files."""
    print("Loading district GeoJSON...")
    with open("src/raw/malaysia.district.geojson", "r") as f:
        geojson = json.load(f)

    dataset_districts = load_dataset_districts()
    print(f"Dataset districts: {len(dataset_districts)}")
    print(f"GeoJSON features: {len(geojson['features'])}")

    # Create output directories
    output_dir = Path("output/geojson")
    districts_dir = output_dir / "districts"
    districts_dir.mkdir(parents=True, exist_ok=True)

    # Track mappings and stats
    processed_count = 0
    skipped_count = 0
    mapped_districts = set()

    # Process each district
    for feature in geojson["features"]:
        original_name = feature["properties"]["name"]
        state_code = feature["properties"]["state"]
        state_name = STATE_CODE_TO_NAME.get(state_code, state_code)

        # Apply mapping
        if original_name in DISTRICT_MAPPING:
            mapped_name = DISTRICT_MAPPING[original_name]
            if mapped_name is None:
                skipped_count += 1
                continue
        else:
            mapped_name = original_name

        # Check if in dataset (handling Sarawak "Bahagian" format)
        if not is_in_dataset(mapped_name, dataset_districts):
            print(f"Warning: {mapped_name} not in dataset (original: {original_name})")
            skipped_count += 1
            continue

        # Update feature properties
        feature["properties"]["district"] = mapped_name
        feature["properties"]["state"] = state_name
        feature["properties"]["original_name"] = original_name

        # Create individual district file
        filename = f"{kebab_case(state_name)}.{kebab_case(mapped_name)}.geojson"
        filepath = districts_dir / filename

        # Create FeatureCollection with single feature
        district_geojson = {
            "type": "FeatureCollection",
            "properties": {
                "district": mapped_name,
                "state": state_name,
                "state_code": state_code,
                "source": "malaysia.district.geojson",
                "original_name": original_name,
            },
            "features": [feature],
        }

        with open(filepath, "w") as f:
            json.dump(district_geojson, f)

        processed_count += 1
        mapped_districts.add(mapped_name)

    print(f"\nProcessed: {processed_count} districts")
    print(f"Skipped: {skipped_count} districts")

    # Check for missing districts
    missing = dataset_districts - mapped_districts
    # Remove "Bahagian X" entries since we mapped them to individual names
    missing = {d for d in missing if not d.startswith("Bahagian ")}
    # Remove known missing (no geometry in GeoJSON)
    known_missing = {
        "DAERAH KECIL MUADZAM SHAH",  # Small district not in GeoJSON
    }
    missing = missing - known_missing

    if missing:
        print(f"\nMissing districts (no geometry): {len(missing)}")
        for d in sorted(missing):
            print(f"  - {d}")

    return mapped_districts


def process_state_geojson():
    """Process state GeoJSON and create individual files."""
    print("\nLoading state GeoJSON...")
    with open("src/raw/malaysia.state.geojson", "r") as f:
        geojson = json.load(f)

    # Create output directory
    output_dir = Path("output/geojson")
    states_dir = output_dir / "states"
    states_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing {len(geojson['features'])} states...")

    for feature in geojson["features"]:
        original_name = feature["properties"]["name"]
        state_code = feature["properties"]["state"]

        # Apply mapping
        mapped_name = STATE_MAPPING.get(original_name, original_name)

        # Update feature properties
        feature["properties"]["state"] = mapped_name
        feature["properties"]["state_code"] = state_code
        feature["properties"]["original_name"] = original_name

        # Create individual state file
        filename = f"{kebab_case(mapped_name)}.geojson"
        filepath = states_dir / filename

        # Create FeatureCollection with single feature
        state_geojson = {
            "type": "FeatureCollection",
            "properties": {
                "state": mapped_name,
                "state_code": state_code,
                "source": "malaysia.state.geojson",
                "original_name": original_name,
            },
            "features": [feature],
        }

        with open(filepath, "w") as f:
            json.dump(state_geojson, f)

        print(f"  Created: {filename}")

    print(f"\nCreated {len(geojson['features'])} state files")


def create_summary(mapped_districts):
    """Create a summary of the processing."""
    summary = {
        "total_states": 16,
        "total_districts_processed": len(mapped_districts),
        "output_directory": "output/geojson/",
        "mappings_applied": {
            "districts": {k: v for k, v in DISTRICT_MAPPING.items() if v is not None},
            "states": STATE_MAPPING,
        },
    }

    summary_path = Path("output/geojson/processing_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved to: {summary_path}")


def main():
    print("=" * 60)
    print("GEOJSON PROCESSING")
    print("=" * 60)

    # Process districts
    mapped_districts = process_district_geojson()

    # Process states
    process_state_geojson()

    # Create summary
    create_summary(mapped_districts)

    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: output/geojson/")
    print(f"  - States: output/geojson/states/ (16 files)")
    print(f"  - Districts: output/geojson/districts/ ({len(mapped_districts)} files)")


if __name__ == "__main__":
    main()
