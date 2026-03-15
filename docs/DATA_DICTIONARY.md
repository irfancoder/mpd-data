# Data Dictionary - Malaysian Property Analysis Views

## Overview
13 Parquet views optimized for DuckDB WASM consumption.

**Total Size:** 11.34 MB  
**Total Rows:** 2,028,786  
**Data Period:** January 2021 - September 2025  
**Coverage:** 401,597 residential property transactions

---

## View Descriptions

### 1. transactions_clean
**Purpose:** Raw cleaned transaction data  
**Rows:** 401,597  
**Size:** 7.20 MB  
**Columns:** 16

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | int | Unique identifier |
| property_type | string | Type of property (e.g., '2 - 2 1/2 Storey Terraced') |
| state | string | Malaysian state (e.g., 'Selangor') |
| district | string | District name (e.g., 'Petaling') |
| mukim | string | Mukim (sub-district) |
| scheme_name | string | Housing area/scheme (e.g., 'Bandar Setia Alam') |
| transaction_date | date | Date of transaction |
| year | int | Transaction year |
| month | int | Transaction month |
| tenure | string | Freehold/Leasehold |
| price_rm | float | Transaction price in RM |
| land_area | float | Land area in sqm |
| floor_area | float | Floor area in sqm |
| price_per_sqm | float | Price per square meter |
| price_per_sqft | float | Price per square foot |
| outlier_flag | string | Outlier classification (if any) |

---

### 2. districts_summary
**Purpose:** District-level aggregated metrics  
**Rows:** 127  
**Size:** 0.03 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| total_transactions | int | Total transaction count |
| median_price | float | Median transaction price |
| price_25th | float | 25th percentile price |
| price_75th | float | 75th percentile price |
| min_price | float | Minimum price |
| max_price | float | Maximum price |
| median_price_per_sqft | float | Median price per sqft |
| price_per_sqft_25th | float | 25th percentile price/sqft |
| price_per_sqft_75th | float | 75th percentile price/sqft |
| median_floor_area | float | Median floor area |
| median_land_area | float | Median land area |
| property_type_breakdown | JSON | Count by property type |

---

### 3. schemes_summary
**Purpose:** Housing scheme/neighborhood metrics  
**Rows:** 9,372  
**Size:** 0.52 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| mukim | string | Mukim name |
| scheme_name | string | Scheme name |
| total_transactions | int | Transaction count |
| median_price | float | Median price |
| price_25th | float | 25th percentile |
| price_75th | float | 75th percentile |
| median_price_per_sqft | float | Median price/sqft |
| price_per_sqft_25th | float | 25th percentile |
| price_per_sqft_75th | float | 75th percentile |
| first_transaction_date | date | First transaction |
| last_transaction_date | date | Last transaction |
| price_volatility | float | Coefficient of variation |
| tenure_breakdown | JSON | Freehold vs leasehold counts |

---

### 4-6. Timeline Views (State/District/Scheme)
**Purpose:** Rolling 12-month price trends

**timeline_rolling_12m_state:** 912 rows, 0.02 MB  
**timeline_rolling_12m_district:** 7,239 rows, 0.10 MB  
**timeline_rolling_12m_scheme:** 1,533,243 rows, 1.94 MB

| Column | Type | Description |
|--------|------|-------------|
| state/district/scheme_name | string | Geographic identifier |
| date | date | Month start date |
| rolling_12m_median_price | float | 12-month rolling median price |
| rolling_12m_median_price_per_sqft | float | 12-month rolling median per sqft |
| rolling_12m_transaction_count | int | Transactions in 12-month window |
| yoy_change_pct | float | Year-over-year change % |
| mom_change_pct | float | Month-over-month change % |
| data_quality_score | string | A/B/C/D based on sample size |

**Data Quality Score:**
- **A:** ≥100 transactions
- **B:** 50-99 transactions
- **C:** 20-49 transactions
- **D:** <20 transactions

---

### 7. price_trends_monthly
**Purpose:** Monthly aggregated trends by district and property type  
**Rows:** 31,144  
**Size:** 0.57 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| property_type | string | Property type |
| year_month | period | Year-month period |
| median_price | float | Median price for month |
| median_price_per_sqft | float | Median price/sqft |
| transaction_count | int | Transactions in month |
| avg_floor_area | float | Average floor area |
| avg_land_area | float | Average land area |
| date | date | Month start date |

---

### 8. affordability_matrix
**Purpose:** Price percentiles by district and property type  
**Rows:** 1,004  
**Size:** 0.10 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| property_type | string | Property type |
| price_p10, price_p25, price_p50, price_p75, price_p90 | float | Price percentiles |
| sqft_p10, sqft_p25, sqft_p50, sqft_p75, sqft_p90 | float | Price/sqft percentiles |
| area_p10, area_p25, area_p50, area_p75, area_p90 | float | Area percentiles |
| total_transactions | int | Total transactions |

---

### 9. property_type_comparison
**Purpose:** Cross-property-type comparison by district  
**Rows:** 1,004  
**Size:** 0.03 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| property_type | string | Property type |
| median_price | float | Median price |
| median_price_per_sqft | float | Median price/sqft |
| transaction_count | int | Transaction count |
| market_share_pct | float | % of district transactions |
| premium_vs_cheapest_pct | float | % premium vs cheapest type |

---

### 10. tenure_analysis
**Purpose:** Freehold vs Leasehold analysis  
**Rows:** 1,004  
**Size:** 0.04 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| property_type | string | Property type |
| freehold_median_price | float | Freehold median price |
| leasehold_median_price | float | Leasehold median price |
| freehold_median_price_per_sqft | float | Freehold median price/sqft |
| leasehold_median_price_per_sqft | float | Leasehold median price/sqft |
| sample_size_freehold | int | Freehold sample size |
| sample_size_leasehold | int | Leasehold sample size |
| freehold_premium_pct | float | Freehold premium % |

---

### 11. hot_areas
**Purpose:** Market activity rankings  
**Rows:** 7,819  
**Size:** 0.25 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| scheme_name | string | Scheme name |
| total_transactions | int | Total transactions |
| median_price | float | Median price |
| first_transaction | date | First transaction date |
| last_transaction | date | Last transaction date |
| months_active | float | Months with transactions |
| activity_score | float | Transactions per month |
| price_growth_6m_pct | float | 6-month price growth % |
| price_growth_1yr_pct | float | 1-year price growth % |
| hotness_score | float | Composite activity score |
| market_hotness_rank | int | Rank by hotness |

---

### 12. spatial_index
**Purpose:** Geographic hierarchy lookup  
**Rows:** 27,308  
**Size:** 0.40 MB

| Column | Type | Description |
|--------|------|-------------|
| state | string | State name |
| district | string | District name |
| mukim | string | Mukim name |
| scheme_name | string | Scheme name |
| transaction_count | int | Total transactions |
| first_transaction | date | First transaction |
| last_transaction | date | Last transaction |
| has_sufficient_data | bool | ≥10 transactions |

---

### 13. outliers_flagged
**Purpose:** Data quality flags  
**Rows:** 7,013  
**Size:** 0.14 MB

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | int | Transaction ID |
| state | string | State name |
| district | string | District name |
| scheme_name | string | Scheme name |
| property_type | string | Property type |
| price_rm | float | Price in RM |
| price_per_sqft | float | Price per sqft |
| floor_area | float | Floor area |
| land_area | float | Land area |
| outlier_flag | string | Type of outlier |
| transaction_date | date | Transaction date |

**Outlier Types:**
- **extreme_high_price:** >RM 5M
- **extreme_low_price:** <RM 50k
- **extreme_price_per_sqft:** >RM 5,000/sqft
- **extreme_low_price_per_sqft:** <RM 100/sqft

---

## Geographic Coverage

**States:** 16 (including Kuala Lumpur, Putrajaya, Labuan)  
**Districts:** 127  
**Mukims:** 1,334  
**Schemes:** 27,308 (9,372 with sufficient data for analysis)

## Data Quality

- **Price coverage:** 100% (401,597 records)
- **Date coverage:** 100% (Jan 2021 - Sep 2025)
- **State mapping:** 100% (all 127 districts mapped)
- **Price per sqft:** 99.99% (401,542 records)
- **Outliers flagged:** 1.75% (7,013 records)

## Usage Notes

1. **Timeline views** use rolling 12-month windows for smoothing
2. **YoY change** compares current 12m window vs 12m from 1 year ago
3. **Data quality scores** help identify reliable trends
4. **JSON columns** (property_type_breakdown, tenure_breakdown) need parsing in DuckDB
5. **Outliers** are flagged but included for transparency
