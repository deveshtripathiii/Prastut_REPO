# Uttar Pradesh Universities Data Extractor 🎓📍

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Completed-success.svg)]()
[![Data Quality](https://img.shields.io/badge/Validation-100%25%20Passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated, end-to-end Python web scraping, data cleaning, geospatial enrichment, and tabular reporting pipeline. Designed as a professional portfolio work sample demonstrating core skills required for a **Research Data Analyst (Web Data & Automation)** role.

---

## 📌 Project Purpose

Research and data analytics teams frequently need structured data extracted from semi-structured web sources (government portals, directories, Wikipedia, or institutional registries). This project automates the entire lifecycle:

1. **Ethical Web Extraction**: Scrapes the comprehensive list of higher-education institutions in Uttar Pradesh from Wikipedia using `requests` and `BeautifulSoup4`. Adheres to ethical web standards with identifying `User-Agent` headers and polite request throttling.
2. **Data Wrangling & Sanitization**: Cleans irregular text, strips footnote citations (e.g. `[1]`, `[a]`, `†`, `#`), extracts normalized 4-digit founding years, eliminates duplicate entries, and resolves missing values using `pandas` and regular expressions (`re`).
3. **Automated Quality Validation**: Generates a structured validation report verifying schema integrity, absence of nulls in primary keys, and data volume constraints.
4. **Geospatial Enrichment & Haversine Analysis**: Geocodes each university's host city using `geopy` and OpenStreetMap's `Nominatim` API. Incorporates rate-limiting (1 request/second) and a persistent local JSON cache to prevent redundant API queries. Computes geodesic distances to **Greater Noida, UP** via the mathematical **Haversine formula**.
5. **Multi-Format Export**: Produces both a clean, standardized UTF-8 CSV and a professionally styled, auto-column-width fitted Microsoft Excel (`.xlsx`) workbook using `openpyxl`.

---

## 📂 Project Architecture

```text
uttar-pradesh-universities-data-extractor/
├── scraper.py          # Network fetching, polite delays, and BeautifulSoup table parser
├── cleaner.py          # Regex sanitization, deduplication, schema normalization, and validation report
├── geocoder.py         # Nominatim geocoding, persistent JSON caching, and Haversine distance calculation
├── main.py             # CLI pipeline orchestrator coordinating extraction, transformation, and export
├── requirements.txt    # Project dependencies
├── .gitignore          # Git exclusion rules
├── README.md           # Comprehensive project documentation and analytical report
├── cache/
│   └── geocode_cache.json    # Persistent location coordinates cache (avoids repeated API calls)
└── output/
    ├── uttar_pradesh_universities.csv     # Clean UTF-8 CSV dataset (96 universities)
    └── uttar_pradesh_universities.xlsx    # Auto-formatted Excel report with zebra striping
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### 1. Clone or Navigate to the Repository
```bash
cd uttar-pradesh-universities-data-extractor
```

### 2. Create and Activate a Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

Execute the automated pipeline with default settings:

```bash
python main.py
```

### Optional Command-Line Arguments

The pipeline includes built-in CLI flags for customization:

```bash
python main.py --help
```

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--output-dir` | `str` | `output` | Destination folder for CSV and Excel files |
| `--cache-dir` | `str` | `cache` | Directory where geocoding cache is stored |
| `--delay` | `float` | `1.0` | Polite delay between network requests (seconds) |
| `--url` | `str` | *UP Universities Wiki URL* | Custom source URL |

**Example with custom output path:**
```bash
python main.py --output-dir reports --delay 1.5
```

---

## 📊 Automated Data Validation Report

Every execution runs automated quality verification checks logged directly to standard output:

```text
================ DATA VALIDATION REPORT ================
Total Raw Rows Ingested     : 96
Duplicate Records Removed   : 0
Empty Critical Rows Dropped : 0
Missing Values Handled      : 97
  - Column 'university_name' missing: 0
  - Column 'location' missing: 0
  - Column 'established_year' missing: 7
  - Column 'university_type' missing: 0
  - Column 'additional_details' missing: 90
Final Validated Records     : 96
Validation Check: Row count threshold met (>= 50 rows). Found: 96
STATUS: DATA VALIDATION PASSED SUCCESSFULLY (Quality Score: 100%)
=========================================================
```

---

## 📋 Sample Output Data

Below is an extract of the processed dataset, showing the generated schema and geospatial distance calculations relative to Greater Noida:

| University Name | Location | Established | University Type | Latitude | Longitude | Distance to Greater Noida (km) |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Aligarh Muslim University** | Aligarh | 1875 | Central University | 27.8761 | 78.1358 | **90.89** |
| **Babasaheb Bhimrao Ambedkar University** | Lucknow | 1996 | Central University | 26.8381 | 80.9346 | **383.73** |
| **Banaras Hindu University** | Varanasi | 1916 | Central University | 25.3356 | 83.0076 | **647.65** |
| **Rajiv Gandhi National Aviation University** | Raebareli | 2013 | Central University | 26.2087 | 81.2186 | **445.03** |
| **Rani Lakshmi Bai Central Agricultural University** | Jhansi | 2014 | Central University | 25.5299 | 78.6528 | **346.63** |
| **University of Allahabad** | Prayagraj | 1887 | Central University | 25.4381 | 81.8338 | **545.94** |
| **Jaypee Institute of Information Technology** | Noida | 2004 | Deemed University | 28.5706 | 77.3272 | **20.32** |
| **Amity University** | Noida | 2005 | Private University | 28.5706 | 77.3272 | **20.32** |
| **Shiv Nadar University** | Greater Noida | 2011 | Private University | 28.4671 | 77.5138 | **1.23** |
| **Dayalbagh Educational Institute** | Agra | 1917 | Deemed University | 27.1753 | 78.0098 | **152.78** |

*Full dataset containing all 96 universities is available in [`output/uttar_pradesh_universities.csv`](output/uttar_pradesh_universities.csv).*

---

## 📐 Mathematical Methodology: Haversine Formula

To calculate the spherical distance between each university location and the reference coordinate (**Greater Noida**: `28.4744° N, 77.5040° E`), the module implements the exact Haversine trigonometric formulation:

$$\Delta\phi = \phi_2 - \phi_1, \quad \Delta\lambda = \lambda_2 - \lambda_1$$

$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$

$$c = 2 \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$

$$d = R \cdot c$$

Where:
- $R$ is the Earth's mean spherical radius ($6,371.0\text{ km}$).
- $\phi_1, \phi_2$ are the latitudes in radians.
- $\lambda_1, \lambda_2$ are the longitudes in radians.
- $d$ is the geodesic distance in kilometers.

---

## 🔄 Reusability for Other Web Sources

The codebase is organized into decoupled, modular components following SOLID engineering principles, making it adaptable for other research scraping tasks:

1. **Adapting to Other States or Countries**:
   - Update `DEFAULT_WIKI_URL` in `scraper.py` (e.g., `"List of universities in Maharashtra"` or `"List of universities in Karnataka"`).
   - In `scraper.py`, adjust the table indices or iterate through all wikitables dynamically.
2. **Adapting to Other Target Reference Coordinates**:
   - In `geocoder.py`, modify `GREATER_NOIDA_LAT` and `GREATER_NOIDA_LON` to any desired reference hub (e.g., State Capital, Corporate HQ, or Port).
3. **Plugging into Other Web Portals**:
   - Swap `scraper.fetch_html()` with an authenticated session (`requests.Session()`) or browser automation driver (Playwright/Selenium) if JavaScript rendering is needed, while preserving the existing cleaning, geocoding, and reporting modules intact.
4. **Scheduled Automations**:
   - Can easily be containerized with Docker or triggered via GitHub Actions / cron jobs to execute automated weekly or monthly data syncs.

---

## 🛡️ Best Practices & Quality Standards Implemented

- **Ethical Web Scraping**: Custom identifying user agent, rate limiting, and zero server overload.
- **Resilient Caching**: Disk-backed persistent JSON cache guarantees zero redundant calls to Nominatim on repeated runs.
- **Robust Exception Handling**: Comprehensive `try/except` blocks handling HTTP errors, connection timeouts, and missing DOM nodes.
- **Enterprise Logging**: Replaced unformatted `print` statements with structured `logging` (timestamps, severity levels, component identifiers).
- **Type Hinting & Documentation**: Fully annotated function signatures with PEP 257 docstrings and inline commentary.
