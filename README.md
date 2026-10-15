# Automated Higher Education Data Extraction & Geospatial Distance Analysis Pipeline 🎓📍
### End-to-End Web Data Engineering, Quality Validation, and Spatial Analytics (Uttar Pradesh, India)

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup-4.11%2B-0B8E36.svg?style=flat)](https://www.crummy.com/software/BeautifulSoup/)
[![Nominatim](https://img.shields.io/badge/Nominatim-Geocoding%20API-4A90E2.svg?style=flat&logo=openstreetmap&logoColor=white)](https://nominatim.openstreetmap.org/)
[![Validation Status](https://img.shields.io/badge/Data%20Validation-100%25%20Passed-brightgreen.svg?style=flat)]()
[![Code Quality](https://img.shields.io/badge/Code%20Style-PEP8%20Compliant-blue.svg?style=flat)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](https://opensource.org/licenses/MIT)

---

## Executive Summary

This project presents an enterprise-grade automated data pipeline designed for **Research Data Analysts (Web Data & Automation)**. It solves the common operational challenge of extracting unstandardized, semi-structured web data from institutional listings, transforming it into an analytically rigorous schema, enriching it with geospatial coordinates, and computing geodesic spatial proximities using the mathematical **Haversine formula**.

The pipeline automatically scrapes all higher education institutions in the state of Uttar Pradesh from Wikipedia, strips citation noise and markup relics, verifies schema constraints through automated validation reports, resolves physical geographic coordinates with rate-limiting and persistent caching, and produces production-ready datasets in both **UTF-8 CSV** and **professionally styled Microsoft Excel (`.xlsx`)** formats.

---

## 📑 Table of Contents
- [Executive Summary](#executive-summary)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Data Pipeline Workflow](#-data-pipeline-workflow)
- [Data Dictionary](#-data-dictionary)
- [Data Cleaning & Validation Scorecard](#-data-cleaning--validation-scorecard)
- [Geospatial Methodology & Haversine Formula](#-geospatial-methodology--haversine-formula)
- [Exploratory Research Insights](#-exploratory-research-insights)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Quickstart Guide](#-installation--quickstart-guide)
- [Command-Line Interface (CLI) Reference](#-command-line-interface-cli-reference)
- [Reusability & Production Extension](#-reusability--production-extension)
- [Author & Submission Note](#-author--submission-note)

---

## 🌟 Key Features

- **Ethical & Polite Web Extraction**: Integrates custom, identifying `User-Agent` headers and configurable request throttling (`time.sleep`) to comply with fair scraping etiquette.
- **Multi-Table Normalization**: Combines independent tabular categories (**Central, State, Private, and Deemed universities**) into a unified schema with explicit categorization.
- **Robust Regular Expression Sanitization**: Systematically eliminates citation marks (e.g., `[1]`, `[47]`, `[a]`), footnote indicators (`†`, `‡`, `#`, `*`), and non-breaking space anomalies (`\xa0`).
- **Automated Data Quality Validation**: Built-in verification engine that checks for primary key integrity, missing values, schema structure, and row volume thresholds ($\ge 50$ rows constraint).
- **Rate-Limited Geocoding & Persistent Disk Caching**: Queries OpenStreetMap's Nominatim API while respecting the strict 1-second rate limit. Employs a persistent JSON cache to ensure zero redundant external API calls on subsequent runs.
- **Great-Circle Distance Computation**: Calculates exact geodesic distances (in kilometers) between host cities and **Greater Noida** using the Haversine trigonometric formulation.
- **Publication-Ready Multi-Format Exports**: Outputs clean UTF-8 CSV and an auto-formatted Excel workbook featuring custom header palettes, zebra-striping, center-aligned metrics, and dynamic column auto-fitting.
- **Zero API Key Dependencies**: Fully functional without requiring paid services, proprietary credentials, or rate-limited commercial tokens.

---

## 🏗 System Architecture

```text
+---------------------------------------------------------------------------------------+
|                                  DATA PIPELINE FLOW                                   |
+---------------------------------------------------------------------------------------+
                                           |
                                  [ 1. WEB SCRAPING ]
                     Wikipedia: List of Universities in Uttar Pradesh
                           (requests + BeautifulSoup4 + delay)
                                           |
                                           v
                                [ 2. DATA CLEANING & RE ]
                        • Strip citation brackets ([1], [a], [edit])
                        • Remove footnote symbols (daggers, hashes #, asterisks)
                        • Extract 4-digit calendar years
                        • Drop duplicates & handle missing fields
                                           |
                                           v
                             [ 3. QUALITY VALIDATION REPORT ]
                        • Check required fields: Non-null checks
                        • Minimum row count constraint (>= 50 rows)
                        • Log status & quality metrics
                                           |
                                           v
                               [ 4. GEOSPATIAL ENRICHMENT ]
                        • Check local persistent cache (geocode_cache.json)
                        • If miss -> geopy Nominatim API (1 req/sec throttled)
                        • Store (latitude, longitude)
                                           |
                                           v
                              [ 5. HAVERSINE DISTANCE MATH ]
                        • Calculate geodesic distance (km) to Greater Noida:
                          (28.4744° N, 77.5040° E)
                                           |
                                           v
                                 [ 6. DUAL EXPORT LAYER ]
                        +---------------------------------------+
                        | 1. uttar_pradesh_universities.csv     |
                        | 2. uttar_pradesh_universities.xlsx    |
                        |    (Auto-column widths, custom styles)|
                        +---------------------------------------+
```

---

## 📖 Data Dictionary

The final dataset contains **96 verified institutional records** with 8 structured attributes:

| Column Name | Data Type | Null Count | Description | Sample Value |
| :--- | :---: | :---: | :--- | :--- |
| `university_name` | `string` | `0` | Normalized legal name of the university | `"Aligarh Muslim University"` |
| `location` | `string` | `0` | Host city or district within Uttar Pradesh | `"Aligarh"` |
| `established_year` | `string` | `0` | Clean 4-digit foundation year (`YYYY` or `"Unknown"`) | `"1875"` |
| `university_type` | `string` | `0` | Classification: Central, State, Private, or Deemed | `"Central University"` |
| `additional_details` | `string` | `0` | Extracted enrollment or status information | `"1920 20791"` / `"Not Specified"` |
| `latitude` | `float` | `0` | Resolved geographical latitude in decimal degrees | `27.876107` |
| `longitude` | `float` | `0` | Resolved geographical longitude in decimal degrees | `78.135815` |
| `distance_from_greater_noida_km` | `float` | `0` | Great-circle Haversine distance to Greater Noida (km) | `90.89` |

---

## 🛡 Data Cleaning & Validation Scorecard

The extraction process includes an automated data quality gate ([`cleaner.py`](file:///cleaner.py)). The pipeline runs assertions before proceeding to spatial enrichment:

```text
================ DATA VALIDATION REPORT ================
Total Raw Rows Ingested     : 96
Duplicate Records Removed   : 0
Empty Critical Rows Dropped : 0
Missing Values Handled      : 97
  - Column 'university_name' missing    : 0
  - Column 'location' missing           : 0
  - Column 'established_year' missing   : 7 (filled with 'Unknown')
  - Column 'university_type' missing    : 0
  - Column 'additional_details' missing : 90 (standardized to 'Not Specified')
Final Validated Records     : 96
Validation Check            : Row count threshold met (96 >= 50 rows)
STATUS                      : DATA VALIDATION PASSED (Quality Score: 100%)
=========================================================
```

### Regular Expression Cleaning Highlights
- **Citation Marks**: `re.sub(r"\[.*?\]", "", text)` strips footnote tags like `[1]`, `[47]`, and `[a]`.
- **Special Markers**: `re.sub(r"[\u2020\u2021\u00b6*#^~§]", "", text)` strips footnote daggers (`†`), section glyphs, and hash markers (`#`).
- **Year Normalization**: `re.search(r"\b(1[7-9]\d{2}|20\d{2})\b", text)` extracts standard 4-digit Gregorian calendar years.
- **Whitespace Sanitation**: Eliminates non-breaking spaces (`\xa0`) and collapses redundant spaces via `re.sub(r"\s+", " ", text).strip()`.

---

## 📐 Geospatial Methodology & Haversine Formula

To calculate geodesic distances on the spherical Earth surface without external commercial routing APIs, the pipeline applies the mathematical **Haversine formula**:

$$\Delta\phi = \phi_2 - \phi_1, \quad \Delta\lambda = \lambda_2 - \lambda_1$$

$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$

$$c = 2 \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$

$$d = R \cdot c$$

**Where:**
- $R = 6,371.0\text{ km}$ (Earth's volumetric mean radius)
- $\phi_1, \phi_2$ are the latitudes of the origin and destination in radians
- $\lambda_1, \lambda_2$ are the longitudes of the origin and destination in radians
- Reference Benchmark (**Greater Noida, UP**): `28.4744° N, 77.5040° E`

### OpenStreetMap Nominatim Rate-Limiting & Caching Architecture
- **Compliance**: Respects OpenStreetMap's usage policy by maintaining a strictly enforced minimum **1.05-second sleep interval** between successive network calls.
- **Local Cache**: Every resolved `(latitude, longitude)` pair is saved in [`cache/geocode_cache.json`](file:///cache/geocode_cache.json).
- **Efficiency**: With 38 distinct cities across 96 institutions, the pipeline performs only 38 network lookups on the first run. All subsequent executions execute with **0 network requests** in approximately **2.1 seconds**.

---

## 📊 Exploratory Research Insights

From an analyst perspective, the extracted dataset reveals several key structural patterns about higher education in Uttar Pradesh:

### 1. Institutional Breakdown by Classification
- **State Universities**: **45** (46.9%) — Forms the largest segment of higher education institutions.
- **Private Universities**: **37** (38.5%) — Highly concentrated in the National Capital Region (NCR).
- **Deemed Universities**: **8** (8.3%) — Specialized technical and deemed research bodies.
- **Central Universities**: **6** (6.2%) — Major federally funded institutions (AMU, BHU, Allahabad, BBAU, RGNAU, RLBCAU).

### 2. Spatial Distance Distribution (Relative to Greater Noida)
- **Minimum Distance**: `1.25 km` (Institutions inside Greater Noida Knowledge Park)
- **25th Percentile**: `110.29 km`
- **Median Distance**: `356.92 km`
- **Mean Distance**: `308.77 km`
- **Maximum Distance**: `715.38 km` (Eastern boundary institutions in Ballia)

### 3. Top Academic Clusters
- **Lucknow**: 15 Universities (State administrative and research capital)
- **Prayagraj**: 7 Universities (Historic educational center)
- **Greater Noida / Noida**: 12 Universities (Major technical & private hub)
- **Meerut**: 6 Universities (Western UP hub)
- **Gorakhpur**: 5 Universities (Eastern UP regional hub)

---

## 📁 Project Directory Structure

```text
uttar-pradesh-universities-data-extractor/
│
├── scraper.py          # Modular web scraper using requests & BeautifulSoup4
├── cleaner.py          # Regex cleaning, year parser, deduplication & validation engine
├── geocoder.py         # Nominatim geocoder client, disk cache & Haversine distance math
├── main.py             # CLI orchestrator coordinating extraction, transformation & export
│
├── requirements.txt    # Frozen dependency specifications
├── .gitignore          # Ignores byte-code, virtualenvs, OS artifacts & caches
├── README.md           # Professional project and analytical documentation
│
├── cache/
│   └── geocode_cache.json   # 38 resolved unique location coordinates
│
└── output/
    ├── uttar_pradesh_universities.csv     # Clean UTF-8 CSV dataset (96 records)
    └── uttar_pradesh_universities.xlsx    # Formatted Excel sheet with auto-column widths
```

---

## 💻 Installation & Quickstart Guide

### Prerequisites
- Python 3.9, 3.10, 3.11, 3.12, 3.13, or 3.14
- `git`

### 1. Clone the Repository
```bash
git clone https://github.com/deveshtripathiii/Prastut_REPO.git
cd Prastut_REPO
```

### 2. Set Up a Virtual Environment
```bash
# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Execute the Automation Pipeline
```bash
python main.py
```

---

## ⚙️ Command-Line Interface (CLI) Reference

The pipeline supports configurable command-line arguments for research workflows:

```bash
python main.py [OPTIONS]
```

| Flag | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `--output-dir` | `str` | `output` | Folder where generated CSV and Excel files will be placed |
| `--cache-dir` | `str` | `cache` | Directory containing `geocode_cache.json` |
| `--delay` | `float` | `1.0` | Politeness sleep duration in seconds before HTTP requests |
| `--url` | `str` | *Default Wiki* | Target URL to extract tabular data from |

**Example: Custom Destination Directory**
```bash
python main.py --output-dir custom_reports --delay 2.0
```

---

## 🔄 Reusability & Production Extension

This architecture was designed with modular, decoupled interfaces to allow rapid adaptation across diverse data analyst projects:

1. **State-Level Portability**:
   - Change `DEFAULT_WIKI_URL` in [`scraper.py`](file:///scraper.py) to target other state lists (e.g., *"List of universities in Maharashtra"*, *"List of universities in Karnataka"*, or *"List of universities in Tamil Nadu"*).
2. **Benchmark Hub Adaptation**:
   - In [`geocoder.py`](file:///geocoder.py), change `GREATER_NOIDA_LAT` and `GREATER_NOIDA_LON` to any corporate office, regional warehouse, capital city, or shipping port to compute new proximity metrics.
3. **Plugging into Other Web Portals**:
   - The modular separation between `scraper.py` and `cleaner.py` allows swapping the HTTP scraper with Selenium, Playwright, or direct REST API collectors without modifying cleaning or geospatial routines.
4. **Scheduled Orchestration**:
   - Can be containerized via Docker or scheduled through **GitHub Actions / Apache Airflow / cron jobs** for periodic automated syncs.

---

## 👤 Author & Submission Note

- **Author**: Devesh Tripathi
- **Repository**: [https://github.com/deveshtripathiii/Prastut_REPO](https://github.com/deveshtripathiii/Prastut_REPO)
- **Role Target**: Research Data Analyst (Web Data and Automation)
- **Sample Output**: Included directly in [`output/`](output/) folder for review.
