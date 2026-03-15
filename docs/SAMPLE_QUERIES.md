# Sample DuckDB Queries for Frontend

## Setup

```javascript
// Initialize DuckDB WASM
const db = new duckdb.AsyncDuckDB();

// Load Parquet files from S3
await db.query(`
  CREATE VIEW districts AS 
  SELECT * FROM 'https://your-s3-bucket/districts_summary.parquet'
`);

await db.query(`
  CREATE VIEW schemes AS 
  SELECT * FROM 'https://your-s3-bucket/schemes_summary.parquet'
`);

await db.query(`
  CREATE VIEW timeline_state AS 
  SELECT * FROM 'https://your-s3-bucket/timeline_rolling_12m_state.parquet'
`);

await db.query(`
  CREATE VIEW timeline_district AS 
  SELECT * FROM 'https://your-s3-bucket/timeline_rolling_12m_district.parquet'
`);

await db.query(`
  CREATE VIEW timeline_scheme AS 
  SELECT * FROM 'https://your-s3-bucket/timeline_rolling_12m_scheme.parquet'
`);
```

---

## 1. "How much should I pay in Area X?"

Get price statistics for a specific housing scheme:

```sql
SELECT 
  scheme_name,
  district,
  state,
  median_price,
  price_25th,
  price_75th,
  median_price_per_sqft,
  total_transactions,
  price_volatility
FROM schemes
WHERE scheme_name = 'Bandar Setia Alam'
  AND state = 'Selangor';
```

**Example Output:**
```
scheme_name: Bandar Setia Alam
district: Klang
state: Selangor
median_price: 485000.00
price_25th: 420000.00
price_75th: 550000.00
median_price_per_sqft: 452.50
total_transactions: 1674
price_volatility: 0.18
```

---

## 2. "What areas fit my budget of RM 500k?"

Find schemes within budget range:

```sql
SELECT 
  state,
  district,
  scheme_name,
  median_price,
  median_price_per_sqft,
  total_transactions
FROM schemes
WHERE median_price BETWEEN 400000 AND 600000
  AND total_transactions >= 20
ORDER BY median_price
LIMIT 50;
```

---

## 3. "Compare districts in Selangor"

Get latest metrics for all districts in a state:

```sql
SELECT 
  district,
  median_price,
  median_price_per_sqft,
  total_transactions
FROM districts
WHERE state = 'Selangor'
ORDER BY median_price DESC;
```

---

## 4. "Price trend for specific scheme over time"

Show rolling 12-month price trend:

```sql
SELECT 
  date,
  rolling_12m_median_price,
  rolling_12m_median_price_per_sqft,
  yoy_change_pct,
  mom_change_pct,
  data_quality_score
FROM timeline_scheme
WHERE scheme_name = 'Bandar Setia Alam'
  AND state = 'Selangor'
  AND data_quality_score IN ('A', 'B', 'C')
ORDER BY date;
```

---

## 5. "State-level market trends"

Compare price trends across states:

```sql
SELECT 
  state,
  date,
  rolling_12m_median_price,
  yoy_change_pct,
  data_quality_score
FROM timeline_state
WHERE state IN ('Selangor', 'Johor', 'Penang', 'Kuala Lumpur')
  AND date >= '2023-01-01'
ORDER BY state, date;
```

---

## 6. "District price trends over time"

Show all districts in a state with trend data:

```sql
SELECT 
  district,
  date,
  rolling_12m_median_price,
  yoy_change_pct,
  data_quality_score
FROM timeline_district
WHERE state = 'Selangor'
  AND date = '2024-12-01'
ORDER BY rolling_12m_median_price DESC;
```

---

## 7. "Affordability by property type"

Get price ranges for different property types:

```sql
SELECT 
  district,
  property_type,
  price_p25,
  price_p50,
  price_p75,
  total_transactions
FROM affordability_matrix
WHERE state = 'Selangor'
  AND total_transactions >= 50
ORDER BY district, price_p50;
```

---

## 8. "Freehold vs Leasehold premium"

Compare tenure types by district:

```sql
SELECT 
  district,
  property_type,
  freehold_median_price,
  leasehold_median_price,
  freehold_premium_pct,
  sample_size_freehold,
  sample_size_leasehold
FROM tenure_analysis
WHERE state = 'Kuala Lumpur'
  AND sample_size_freehold >= 10
  AND sample_size_leasehold >= 10
ORDER BY freehold_premium_pct DESC
LIMIT 20;
```

---

## 9. "Hottest areas by activity"

Find most active markets:

```sql
SELECT 
  state,
  district,
  scheme_name,
  median_price,
  activity_score,
  price_growth_6m_pct,
  price_growth_1yr_pct,
  market_hotness_rank
FROM hot_areas
WHERE state = 'Selangor'
ORDER BY market_hotness_rank
LIMIT 20;
```

---

## 10. "Property type comparison in district"

Compare different property types:

```sql
SELECT 
  property_type,
  median_price,
  median_price_per_sqft,
  transaction_count,
  market_share_pct,
  premium_vs_cheapest_pct
FROM property_type_comparison
WHERE district = 'Petaling'
ORDER BY median_price;
```

---

## 11. "Search schemes by name"

Fuzzy search for schemes:

```sql
SELECT 
  state,
  district,
  scheme_name,
  median_price,
  total_transactions
FROM schemes
WHERE scheme_name ILIKE '%setia%'
ORDER BY total_transactions DESC
LIMIT 20;
```

---

## 12. "Get geographic hierarchy"

Navigate state → district → scheme:

```sql
-- Get all states
SELECT DISTINCT state FROM districts ORDER BY state;

-- Get districts in state
SELECT district, total_transactions, median_price
FROM districts
WHERE state = 'Selangor'
ORDER BY median_price DESC;

-- Get schemes in district
SELECT scheme_name, median_price, total_transactions
FROM schemes
WHERE district = 'Petaling'
  AND state = 'Selangor'
ORDER BY total_transactions DESC
LIMIT 20;
```

---

## 13. "Filter out outliers"

Get clean data without extreme values:

```sql
SELECT *
FROM transactions_clean
WHERE district = 'Petaling'
  AND property_type = 'Condominium/Apartment'
  AND outlier_flag IS NULL
  AND price_rm BETWEEN 200000 AND 1000000
LIMIT 100;
```

---

## 14. "Calculate custom aggregations"

Create your own metrics:

```sql
SELECT 
  state,
  district,
  COUNT(*) as transaction_count,
  MEDIAN(price_rm) as median_price,
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price_rm) as price_25th,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price_rm) as price_75th,
  AVG(price_per_sqft) as avg_price_per_sqft
FROM transactions_clean
WHERE outlier_flag IS NULL
  AND transaction_date >= '2024-01-01'
GROUP BY state, district
HAVING COUNT(*) >= 10
ORDER BY median_price DESC;
```

---

## 15. "Time series chart data"

Get data for line charts:

```sql
-- State trends for chart
SELECT 
  date,
  MAX(CASE WHEN state = 'Selangor' THEN rolling_12m_median_price END) as selangor_price,
  MAX(CASE WHEN state = 'Johor' THEN rolling_12m_median_price END) as johor_price,
  MAX(CASE WHEN state = 'Penang' THEN rolling_12m_median_price END) as penang_price
FROM timeline_state
WHERE date >= '2022-01-01'
GROUP BY date
ORDER BY date;
```

---

## Performance Tips

1. **Filter early** - Apply WHERE clauses before aggregations
2. **Use views** - Pre-filtered views are faster than raw data
3. **Limit results** - Use LIMIT for UI pagination
4. **Index columns** - DuckDB automatically indexes Parquet files
5. **Cache results** - Cache frequent queries in frontend state

## Data Quality Filters

Always consider data quality in your queries:

```sql
-- Good quality data only
WHERE data_quality_score IN ('A', 'B')

-- Sufficient sample size
WHERE total_transactions >= 20

-- Recent data only
WHERE date >= '2023-01-01'

-- Exclude outliers
WHERE outlier_flag IS NULL
```
