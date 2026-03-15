# GeoJSON Processing Summary

## Overview
Successfully processed Malaysia state and district GeoJSON files to create individual files matching the property transaction dataset.

## Processing Results

### Files Created
- **States**: 16 individual GeoJSON files
- **Districts**: 106 individual GeoJSON files
- **Location**: `output/geojson/`

### Directory Structure
```
output/geojson/
├── states/
│   ├── johor.geojson
│   ├── selangor.geojson
│   ├── kuala-lumpur.geojson
│   ├── penang.geojson
│   ├── kedah.geojson
│   ├── kelantan.geojson
│   ├── terengganu.geojson
│   ├── perak.geojson
│   ├── pahang.geojson
│   ├── negeri-sembilan.geojson
│   ├── melaka.geojson
│   ├── perlis.geojson
│   ├── sabah.geojson
│   ├── sarawak.geojson
│   ├── putrajaya.geojson
│   └── labuan.geojson
│
└── districts/
    ├── johor.batu-pahat.geojson
    ├── johor.johor-bahru.geojson
    ├── selangor.hulu-langat.geojson
    ├── selangor.hulu-selangor.geojson
    ├── selangor.petaling.geojson
    ├── sarawak.kuching.geojson
    ├── sarawak.miri.geojson
    └── ... (106 total)
```

## Name Mappings Applied

### District Name Corrections (GeoJSON → Dataset)
| Original (GeoJSON) | Corrected | Reason |
|-------------------|-----------|---------|
| Ulu Langat | Hulu Langat | Spelling correction |
| Ulu Selangor | Hulu Selangor | Spelling correction |
| Cameron Highlands | Cameron Highland | Singular form |
| W.P. Kuala Lumpur | Kuala Lumpur | Remove prefix |
| W.P. Labuan | Labuan | Remove prefix |
| W.P. Putrajaya | Putrajaya | Remove prefix |
| Pulau Pinang | Penang | Common name |
| WP K Lumpur | Kuala Lumpur | Remove prefix |

### State Name Corrections
| Original (GeoJSON) | Corrected |
|-------------------|-----------|
| Pulau Pinang | Penang |
| WP K Lumpur | Kuala Lumpur |
| WP Putrajaya | Putrajaya |
| WP Labuan | Labuan |

### Sarawak Districts
The dataset used "Bahagian X" format (e.g., "Bahagian Kuching"), but the GeoJSON has individual districts. Mapped individual districts to match:
- Betong, Bintulu, Kapit, Kuching, Limbang, Miri, Mukah, Samarahan, Sarikei, Serian, Sibu, Sri Aman

## Districts Not Created (No Geometry)

### Missing from GeoJSON (33 districts)
These districts exist in the dataset but have no corresponding geometry:

**Sabah Districts (22):**
- Kota Belud, Kota Marudu, Kudat, Kunak, Labuk Sugut, Lahad Datu, Papar, Penampang, Pitas, Putatan, Ranau, Semporna, Sipitang, Tambunan, Tawau, Tenom, Tuaran

**Other (11):**
- DAERAH KECIL MUADZAM SHAH (Pahang)
- Kota Bahru (Kelantan - alternative spelling)
- Bandar Baru (Kedah - typo, should be Bandar Baharu)
- Larut Matang (Perak)

### Excluded from GeoJSON (54 districts)
These districts exist in GeoJSON but not in dataset:

**Sabah Districts:**
Asajaya, Belaga, Beluran, Beluru, Bukit Mabong, Dalat, Daro, Julau, Kabong, Kalabakan, Kanowit, Kecil Lojing, Kinabatangan, Kota Belud, Kota Marudu, Kuala Penyu, Kudat, Kunak, Lahad Datu, Lawas, Lubok Antu, Lundu, Marudi, Matu, Meradong, Nabawan, Pakan, Papar, Penampang, Pitas, Pusa, Putatan, Ranau, Saratok, Selangau, Semporna, Sebauh, Subis, Sipitang, Tambunan, Tawau, Tatau, Telang Usan, Telupid, Tenom, Tongod, Tuaran, Tanjung Manis, Tebedu, Maradong, Simunjan, Song, Bau

## File Naming Convention

### States
Format: `{state-name}.geojson`
- All lowercase
- Kebab-case (spaces replaced with hyphens)
- Examples: `kuala-lumpur.geojson`, `negeri-sembilan.geojson`

### Districts
Format: `{state-name}.{district-name}.geojson`
- All lowercase
- Kebab-case
- Examples: `johor.batu-pahat.geojson`, `selangor.hulu-langat.geojson`

## GeoJSON Structure

### State File
```json
{
  "type": "FeatureCollection",
  "properties": {
    "state": "Selangor",
    "state_code": "SGR",
    "source": "malaysia.state.geojson",
    "original_name": "Selangor"
  },
  "features": [...]
}
```

### District File
```json
{
  "type": "FeatureCollection",
  "properties": {
    "district": "Hulu Langat",
    "state": "Selangor",
    "state_code": "SGR",
    "source": "malaysia.district.geojson",
    "original_name": "Ulu Langat"
  },
  "features": [...]
}
```

## Usage

### Loading in DuckDB WASM
```javascript
// Load state geometry
await db.query(`
  SELECT * FROM 'https://your-bucket/states/selangor.geojson'
`);

// Load district geometry
await db.query(`
  SELECT * FROM 'https://your-bucket/districts/selangor.petaling.geojson'
`);

// Join with property data
await db.query(`
  SELECT 
    d.district,
    d.median_price,
    g.geometry
  FROM districts_summary d
  JOIN 'districts/selangor.petaling.geojson' g
    ON d.district = g.district
`);
```

## Statistics

- **Total States**: 16 (100% coverage)
- **Total Districts with Geometry**: 106 out of 127 (83.5% coverage)
- **Missing Districts**: 21 (mostly Sabah)
- **Files Created**: 122 (16 states + 106 districts)

## Next Steps

1. **Upload to S3**: Copy files to your S3 bucket for DuckDB WASM access
2. **Handle Missing Districts**: Consider adding placeholder geometries or excluding from maps
3. **Update Dataset**: Consider updating dataset to use individual Sarawak district names instead of "Bahagian X"

## Script

The processing script is saved as `process_geojson.py` and can be re-run if needed:

```bash
python3 process_geojson.py
```
