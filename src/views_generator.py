"""Main orchestrator for generating all Parquet views."""

import pandas as pd
import os
import json
from typing import Dict
from src.config import OUTPUT_DIR
from src.data_loader import load_and_clean_data
from src.transformers import (
    create_transactions_clean_view,
    create_districts_summary_view,
    create_schemes_summary_view,
    create_affordability_matrix_view,
    create_property_type_comparison_view,
    create_tenure_analysis_view,
    create_spatial_index_view,
    create_outliers_flagged_view,
)
from src.aggregations import (
    create_timeline_state_view,
    create_timeline_district_view,
    create_timeline_scheme_view,
    create_price_trends_monthly_view,
    create_hot_areas_view,
)


class ViewsGenerator:
    """Orchestrates the generation of all Parquet views."""

    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        self.df = None
        self.views = {}

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def load_data(self, input_file: str = None) -> "ViewsGenerator":
        """Load and clean raw data."""
        print("=" * 60)
        print("STEP 1: Loading and cleaning data")
        print("=" * 60)
        self.df = load_and_clean_data(input_file)
        return self

    def generate_view(self, name: str, create_func) -> "ViewsGenerator":
        """Generate a single view."""
        print(f"\nGenerating {name}...")
        try:
            view = create_func(self.df)
            self.views[name] = view
            print(f"  ✓ Generated {name}: {len(view):,} rows")
            return self
        except Exception as e:
            print(f"  ✗ Error generating {name}: {e}")
            raise

    def generate_all_views(self) -> "ViewsGenerator":
        """Generate all 13 views."""
        print("\n" + "=" * 60)
        print("STEP 2: Generating views")
        print("=" * 60)

        # Core views
        self.generate_view("transactions_clean", create_transactions_clean_view)
        self.generate_view("districts_summary", create_districts_summary_view)
        self.generate_view("schemes_summary", create_schemes_summary_view)

        # Timeline views
        self.generate_view("timeline_rolling_12m_state", create_timeline_state_view)
        self.generate_view(
            "timeline_rolling_12m_district", create_timeline_district_view
        )
        self.generate_view("timeline_rolling_12m_scheme", create_timeline_scheme_view)

        # Analysis views
        self.generate_view("price_trends_monthly", create_price_trends_monthly_view)
        self.generate_view("affordability_matrix", create_affordability_matrix_view)
        self.generate_view(
            "property_type_comparison", create_property_type_comparison_view
        )
        self.generate_view("tenure_analysis", create_tenure_analysis_view)
        self.generate_view("hot_areas", create_hot_areas_view)
        self.generate_view("spatial_index", create_spatial_index_view)
        self.generate_view("outliers_flagged", create_outliers_flagged_view)

        return self

    def save_views(self) -> "ViewsGenerator":
        """Save all views as Parquet files."""
        print("\n" + "=" * 60)
        print("STEP 3: Saving views to Parquet")
        print("=" * 60)

        for name, view in self.views.items():
            filepath = os.path.join(self.output_dir, f"{name}.parquet")
            print(f"\nSaving {name}...")

            try:
                # Convert dict columns to JSON strings for Parquet compatibility
                view_to_save = view.copy()
                for col in view_to_save.columns:
                    if view_to_save[col].dtype == "object":
                        # Check if column contains dictionaries
                        sample = (
                            view_to_save[col].dropna().iloc[0]
                            if len(view_to_save[col].dropna()) > 0
                            else None
                        )
                        if isinstance(sample, dict):
                            view_to_save[col] = view_to_save[col].apply(
                                lambda x: json.dumps(x) if isinstance(x, dict) else x
                            )

                view_to_save.to_parquet(
                    filepath, engine="pyarrow", compression="snappy", index=False
                )

                # Get file size
                file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  ✓ Saved to {filepath}")
                print(f"    Size: {file_size_mb:.2f} MB")
                print(f"    Rows: {len(view_to_save):,}")
                print(f"    Columns: {len(view_to_save.columns)}")

            except Exception as e:
                print(f"  ✗ Error saving {name}: {e}")
                raise

        return self

    def generate_summary(self) -> Dict:
        """Generate summary of all views."""
        summary = {"total_views": len(self.views), "views": {}}

        total_rows = 0
        total_size_mb = 0

        for name, view in self.views.items():
            filepath = os.path.join(self.output_dir, f"{name}.parquet")
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

            summary["views"][name] = {
                "rows": len(view),
                "columns": len(view.columns),
                "file_size_mb": round(file_size_mb, 2),
            }

            total_rows += len(view)
            total_size_mb += file_size_mb

        summary["total_rows"] = total_rows
        summary["total_size_mb"] = round(total_size_mb, 2)

        return summary

    def run(self, input_file: str = None) -> Dict:
        """Run complete pipeline."""
        print("\n" + "=" * 60)
        print("MALAYSIAN PROPERTY ANALYSIS - VIEW GENERATION")
        print("=" * 60)

        self.load_data(input_file)
        self.generate_all_views()
        self.save_views()

        summary = self.generate_summary()

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"\nTotal views generated: {summary['total_views']}")
        print(f"Total rows across all views: {summary['total_rows']:,}")
        print(f"Total file size: {summary['total_size_mb']:.2f} MB")
        print(f"\nOutput directory: {self.output_dir}")

        return summary


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Parquet views for Malaysian property analysis"
    )
    parser.add_argument("--input", "-i", help="Input CSV file path", default=None)
    parser.add_argument(
        "--output", "-o", help="Output directory for Parquet files", default=OUTPUT_DIR
    )

    args = parser.parse_args()

    generator = ViewsGenerator(output_dir=args.output)
    summary = generator.run(input_file=args.input)

    # Save summary as JSON
    summary_path = os.path.join(args.output, "generation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()
