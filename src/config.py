"""Configuration and mappings for property data pipeline."""

# District to State mapping (127 districts mapped to 16 states/territories)
DISTRICT_TO_STATE = {
    # Johor (10 districts)
    "Batu Pahat": "Johor",
    "Johor Bahru": "Johor",
    "Kluang": "Johor",
    "Kota Tinggi": "Johor",
    "Kulai": "Johor",
    "Mersing": "Johor",
    "Muar": "Johor",
    "Pontian": "Johor",
    "Segamat": "Johor",
    "Tangkak": "Johor",
    # Selangor (9 districts)
    "Gombak": "Selangor",
    "Hulu Langat": "Selangor",
    "Hulu Selangor": "Selangor",
    "Klang": "Selangor",
    "Kuala Langat": "Selangor",
    "Kuala Selangor": "Selangor",
    "Petaling": "Selangor",
    "Sabak Bernam": "Selangor",
    "Sepang": "Selangor",
    # Kuala Lumpur
    "Kuala Lumpur": "Kuala Lumpur",
    # Putrajaya
    "Putrajaya": "Putrajaya",
    # Labuan
    "Labuan": "Labuan",
    # Perlis
    "Kangar": "Perlis",
    "Perlis": "Perlis",
    # Kedah (12 districts)
    "Baling": "Kedah",
    "Bandar Baharu": "Kedah",
    "Kota Setar": "Kedah",
    "Kuala Muda": "Kedah",
    "Kubang Pasu": "Kedah",
    "Kulim": "Kedah",
    "Langkawi": "Kedah",
    "Padang Terap": "Kedah",
    "Pendang": "Kedah",
    "Pokok Sena": "Kedah",
    "Sik": "Kedah",
    "Yan": "Kedah",
    # Kelantan (10 districts)
    "Bachok": "Kelantan",
    "Gua Musang": "Kelantan",
    "Jeli": "Kelantan",
    "Kota Bharu": "Kelantan",
    "Kuala Krai": "Kelantan",
    "Machang": "Kelantan",
    "Pasir Mas": "Kelantan",
    "Pasir Puteh": "Kelantan",
    "Tanah Merah": "Kelantan",
    "Tumpat": "Kelantan",
    # Terengganu (8 districts)
    "Besut": "Terengganu",
    "Dungun": "Terengganu",
    "Hulu Terengganu": "Terengganu",
    "Kemaman": "Terengganu",
    "Kuala Nerus": "Terengganu",
    "Kuala Terengganu": "Terengganu",
    "Marang": "Terengganu",
    "Setiu": "Terengganu",
    # Penang (5 districts)
    "Barat Daya": "Penang",
    "Seberang Perai Selatan": "Penang",
    "Seberang Perai Tengah": "Penang",
    "Seberang Perai Utara": "Penang",
    "Timur Laut": "Penang",
    # Perak (12 districts)
    "Batang Padang": "Perak",
    "Hilir Perak": "Perak",
    "Hulu Perak": "Perak",
    "Kampar": "Perak",
    "Kerian": "Perak",
    "Kinta": "Perak",
    "Kuala Kangsar": "Perak",
    "Larut Matang": "Perak",
    "Manjung": "Perak",
    "Muallim": "Perak",
    "Perak Tengah": "Perak",
    "Selama": "Perak",
    # Pahang (11 districts)
    "Bentong": "Pahang",
    "Bera": "Pahang",
    "Cameron Highland": "Pahang",
    "Jerantut": "Pahang",
    "Kuantan": "Pahang",
    "Lipis": "Pahang",
    "Maran": "Pahang",
    "Pekan": "Pahang",
    "Raub": "Pahang",
    "Rompin": "Pahang",
    "Temerloh": "Pahang",
    # Melaka (3 districts)
    # Melaka (3 districts)
    "Alor Gajah": "Melaka",
    "Jasin": "Melaka",
    "Melaka Tengah": "Melaka",
    # Negeri Sembilan (7 districts)
    "Jelebu": "Negeri Sembilan",
    "Jempol": "Negeri Sembilan",
    "Kuala Pilah": "Negeri Sembilan",
    "Port Dickson": "Negeri Sembilan",
    "Rembau": "Negeri Sembilan",
    "Seremban": "Negeri Sembilan",
    "Tampin": "Negeri Sembilan",
    # Sabah (25 districts)
    "Beaufort": "Sabah",
    "Beluran": "Sabah",
    "Keningau": "Sabah",
    "Kinabatangan": "Sabah",
    "Kota Belud": "Sabah",
    "Kota Kinabalu": "Sabah",
    "Kota Marudu": "Sabah",
    "Kuala Penyu": "Sabah",
    "Kudat": "Sabah",
    "Kunak": "Sabah",
    "Lahad Datu": "Sabah",
    "Nabawan": "Sabah",
    "Papar": "Sabah",
    "Penampang": "Sabah",
    "Pitas": "Sabah",
    "Putatan": "Sabah",
    "Ranau": "Sabah",
    "Sandakan": "Sabah",
    "Semporna": "Sabah",
    "Sipitang": "Sabah",
    "Tambunan": "Sabah",
    "Tawau": "Sabah",
    "Telupid": "Sabah",
    "Tenom": "Sabah",
    "Tongod": "Sabah",
    "Tuaran": "Sabah",
    # Sarawak (12 divisions treated as districts) - using individual names (GeoJSON format)
    "Betong": "Sarawak",
    "Bintulu": "Sarawak",
    "Kapit": "Sarawak",
    "Kuching": "Sarawak",
    "Limbang": "Sarawak",
    "Miri": "Sarawak",
    "Mukah": "Sarawak",
    "Samarahan": "Sarawak",
    "Sarikei": "Sarawak",
    "Serian": "Sarawak",
    "Sibu": "Sarawak",
    "Sri Aman": "Sarawak",
    # Data quality issues - map typos/alternatives
    "Bandar Baharu": "Kedah",
    "Bagan Datuk": "Perak",
    "Kota Bharu": "Kelantan",
}

# Data quality thresholds
MIN_TRANSACTIONS_FOR_SCHEME_SUMMARY = 10
MIN_TRANSACTIONS_FOR_SCHEME_TIMELINE = 20
MIN_TRANSACTIONS_PER_MONTH_FOR_TIMELINE = 3

# Price outlier thresholds
PRICE_OUTLIER_HIGH_THRESHOLD = 5_000_000  # RM 5M
PRICE_OUTLIER_LOW_THRESHOLD = 50_000  # RM 50k

# Date range
DATA_START_DATE = "2021-01-01"
DATA_END_DATE = "2025-09-30"

# Output paths
OUTPUT_DIR = "/Users/irfanismail/Documents/work/irama-data/output/parquet"
INPUT_FILE = "/Users/irfanismail/Documents/work/irama-data/src/raw/Open Transaction Data_Residential.csv"
