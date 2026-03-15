# Malaysian Property Analysis Tool

Transform raw Malaysian property transaction data into optimized Parquet views for DuckDB WASM consumption.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate all views
python generate_views.py

# Output will be in output/parquet/
```

## Views Generated

1. **transactions_clean** - Core cleaned transaction data
2. **districts_summary** - District-level aggregated metrics
3. **schemes_summary** - Housing scheme/neighborhood metrics
4. **timeline_rolling_12m_state** - State-level rolling 12-month trends
5. **timeline_rolling_12m_district** - District-level rolling trends
6. **timeline_rolling_12m_scheme** - Scheme-level rolling trends
7. **price_trends_monthly** - Monthly aggregated trends
8. **affordability_matrix** - Price percentiles by district/property type
9. **property_type_comparison** - Cross-property-type comparison
10. **tenure_analysis** - Freehold vs leasehold analysis
11. **hot_areas** - Market activity rankings
12. **spatial_index** - Geographic hierarchy lookup
13. **outliers_flagged** - Data quality flags

## Data Source

- File: `Open Transaction Data_Residential.csv`
- Records: ~401,597 transactions
- Period: January 2021 - September 2025
- Coverage: Residential properties across Malaysia

## Architecture

- **No backend API** - Frontend queries Parquet files directly via DuckDB WASM
- **Optimized views** - Pre-computed aggregations for fast queries
- **Three-level hierarchy** - State → District → Scheme
