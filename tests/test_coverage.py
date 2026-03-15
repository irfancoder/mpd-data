#!/usr/bin/env python3
"""
Coverage test to verify Parquet and GeoJSON datasets are in sync.

Usage:
    python3 tests/test_coverage.py
"""

import pandas as pd
import json
from pathlib import Path
from typing import Set, Tuple
import sys


class CoverageTest:
    """Test coverage between Parquet and GeoJSON datasets."""

    def __init__(self):
        self.parquet_dir = Path("output/parquet")
        self.geojson_dir = Path("output/geojson/districts")
        self.errors = []
        self.warnings = []

    def load_parquet_districts(self) -> Set[str]:
        """Load unique districts from districts_summary.parquet."""
        filepath = self.parquet_dir / "districts_summary.parquet"
        if not filepath.exists():
            self.errors.append(f"Parquet file not found: {filepath}")
            return set()

        df = pd.read_parquet(filepath)
        return set(df["district"].unique())

    def load_parquet_states(self) -> Set[str]:
        """Load unique states from districts_summary.parquet."""
        filepath = self.parquet_dir / "districts_summary.parquet"
        if not filepath.exists():
            return set()

        df = pd.read_parquet(filepath)
        return set(df["state"].unique())

    def load_geojson_districts(self) -> Set[str]:
        """Load unique districts from GeoJSON filenames."""
        if not self.geojson_dir.exists():
            self.errors.append(f"GeoJSON directory not found: {self.geojson_dir}")
            return set()

        districts = set()
        for f in self.geojson_dir.glob("*.geojson"):
            parts = f.stem.split(".")
            if len(parts) >= 2:
                # Convert kebab-case to title case
                district = " ".join(parts[1:]).replace("-", " ").title()
                districts.add(district)

        return districts

    def load_geojson_states(self) -> Set[str]:
        """Load unique states from GeoJSON state files."""
        states_dir = Path("output/geojson/states")
        if not states_dir.exists():
            return set()

        states = set()
        for f in states_dir.glob("*.geojson"):
            # Convert kebab-case to title case
            state = f.stem.replace("-", " ").title()
            # Fix special cases
            state_map = {
                "Kuala Lumpur": "Kuala Lumpur",
                "Negeri Sembilan": "Negeri Sembilan",
            }
            state = state_map.get(state, state)
            states.add(state)

        return states

    def test_district_coverage(self) -> bool:
        """Test that all parquet districts have GeoJSON files."""
        print("\n" + "=" * 60)
        print("TEST: District Coverage")
        print("=" * 60)

        parquet_districts = self.load_parquet_districts()
        geojson_districts = self.load_geojson_districts()

        print(f"Parquet districts: {len(parquet_districts)}")
        print(f"GeoJSON districts: {len(geojson_districts)}")

        missing_geojson = parquet_districts - geojson_districts
        extra_geojson = geojson_districts - parquet_districts

        if missing_geojson:
            self.errors.append(
                f"Districts in Parquet but missing GeoJSON ({len(missing_geojson)}): {sorted(missing_geojson)}"
            )
            print(f"\n❌ FAIL: {len(missing_geojson)} districts missing GeoJSON:")
            for d in sorted(missing_geojson):
                print(f"  - {d}")
        else:
            print("\n✅ All Parquet districts have GeoJSON files!")

        if extra_geojson:
            self.warnings.append(
                f"Districts with GeoJSON but not in Parquet ({len(extra_geojson)}): {sorted(extra_geojson)}"
            )
            print(f"\n⚠️  WARNING: {len(extra_geojson)} extra GeoJSON files:")
            for d in sorted(extra_geojson):
                print(f"  - {d}")

        matching = len(parquet_districts & geojson_districts)
        coverage = (matching / len(parquet_districts) * 100) if parquet_districts else 0
        print(f"\nCoverage: {matching}/{len(parquet_districts)} ({coverage:.1f}%)")

        return len(missing_geojson) == 0

    def test_state_coverage(self) -> bool:
        """Test that all parquet states have GeoJSON files."""
        print("\n" + "=" * 60)
        print("TEST: State Coverage")
        print("=" * 60)

        parquet_states = self.load_parquet_states()
        geojson_states = self.load_geojson_states()

        print(f"Parquet states: {len(parquet_states)}")
        print(f"GeoJSON states: {len(geojson_states)}")

        missing_geojson = parquet_states - geojson_states
        extra_geojson = geojson_states - parquet_states

        if missing_geojson:
            self.errors.append(
                f"States in Parquet but missing GeoJSON ({len(missing_geojson)}): {sorted(missing_geojson)}"
            )
            print(f"\n❌ FAIL: {len(missing_geojson)} states missing GeoJSON:")
            for s in sorted(missing_geojson):
                print(f"  - {s}")
        else:
            print("\n✅ All Parquet states have GeoJSON files!")

        if extra_geojson:
            self.warnings.append(
                f"States with GeoJSON but not in Parquet ({len(extra_geojson)}): {sorted(extra_geojson)}"
            )
            print(f"\n⚠️  WARNING: {len(extra_geojson)} extra GeoJSON files:")
            for s in sorted(extra_geojson):
                print(f"  - {s}")

        matching = len(parquet_states & geojson_states)
        coverage = (matching / len(parquet_states) * 100) if parquet_states else 0
        print(f"\nCoverage: {matching}/{len(parquet_states)} ({coverage:.1f}%)")

        return len(missing_geojson) == 0

    def test_district_state_consistency(self) -> bool:
        """Test that district-state pairs are consistent between datasets."""
        print("\n" + "=" * 60)
        print("TEST: District-State Consistency")
        print("=" * 60)

        # Load parquet data
        parquet_file = self.parquet_dir / "districts_summary.parquet"
        if not parquet_file.exists():
            print("❌ SKIP: Parquet file not found")
            return True

        df = pd.read_parquet(parquet_file)
        parquet_pairs = set(zip(df["state"], df["district"]))

        # Load GeoJSON data
        geojson_pairs = set()
        for f in self.geojson_dir.glob("*.geojson"):
            with open(f) as fp:
                data = json.load(fp)
                state = data.get("properties", {}).get("state", "")
                district = data.get("properties", {}).get("district", "")
                if state and district:
                    geojson_pairs.add((state, district))

        print(f"Parquet district-state pairs: {len(parquet_pairs)}")
        print(f"GeoJSON district-state pairs: {len(geojson_pairs)}")

        # Check for mismatches
        mismatches = []
        for state, district in parquet_pairs:
            if (state, district) not in geojson_pairs:
                mismatches.append((state, district))

        if mismatches:
            self.errors.append(
                f"District-state pairs in Parquet but not in GeoJSON ({len(mismatches)}): {mismatches[:10]}..."
            )
            print(f"\n❌ FAIL: {len(mismatches)} inconsistent pairs:")
            for state, district in mismatches[:10]:
                print(f"  - {district}, {state}")
            if len(mismatches) > 10:
                print(f"  ... and {len(mismatches) - 10} more")
            return False
        else:
            print("\n✅ All district-state pairs are consistent!")
            return True

    def test_geojson_properties(self) -> bool:
        """Test that GeoJSON files have required properties."""
        print("\n" + "=" * 60)
        print("TEST: GeoJSON Properties")
        print("=" * 60)

        required_props = ["district", "state", "state_code"]
        missing_props = []

        for f in self.geojson_dir.glob("*.geojson"):
            with open(f) as fp:
                data = json.load(fp)
                props = data.get("properties", {})
                for prop in required_props:
                    if prop not in props:
                        missing_props.append((f.name, prop))

        if missing_props:
            self.errors.append(
                f"GeoJSON files missing required properties ({len(missing_props)})"
            )
            print(f"\n❌ FAIL: {len(missing_props)} missing properties:")
            for filename, prop in missing_props[:10]:
                print(f"  - {filename}: missing '{prop}'")
            if len(missing_props) > 10:
                print(f"  ... and {len(missing_props) - 10} more")
            return False
        else:
            print(
                f"\n✅ All {len(list(self.geojson_dir.glob('*.geojson')))} GeoJSON files have required properties!"
            )
            return True

    def run_all_tests(self) -> bool:
        """Run all coverage tests."""
        print("\n" + "=" * 60)
        print("COVERAGE TEST SUITE")
        print("=" * 60)

        tests = [
            ("District Coverage", self.test_district_coverage),
            ("State Coverage", self.test_state_coverage),
            ("District-State Consistency", self.test_district_state_consistency),
            ("GeoJSON Properties", self.test_geojson_properties),
        ]

        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                self.errors.append(f"Test '{name}' failed with exception: {e}")
                results.append((name, False))

        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
            return False
        else:
            print("\n✅ All tests passed!")
            return True


def main():
    """Main entry point."""
    test = CoverageTest()
    success = test.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
