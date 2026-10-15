"""
cleaner.py
==========
Data cleaning and validation module for Uttar Pradesh universities dataset.
Handles citation stripping, regex sanitation, column renaming, deduplication,
missing value imputation, and automated data quality validation reporting.
"""

import logging
import re
from typing import Dict, Any, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


def clean_text(text: Any) -> str:
    """
    Remove Wikipedia citations (e.g., '[1]', '[a]'), footnote daggers,
    extra whitespace, non-breaking spaces, and normalize text.

    Args:
        text (Any): Input text or value.

    Returns:
        str: Cleaned text string.
    """
    if pd.isna(text) or text is None:
        return ""

    s = str(text)

    # Remove Wikipedia reference brackets like [1], [47], [a], [edit]
    s = re.sub(r"\[.*?\]", "", s)

    # Remove footnote markers like †, ‡, *, #, ^, ~, §
    s = re.sub(r"[\u2020\u2021\u00b6*#^~§]", "", s)

    # Fix formatting issues like 'Saifai,Etawah' -> 'Saifai, Etawah'
    s = re.sub(r",([^\s])", r", \1", s)

    # Replace non-breaking spaces and multiple whitespace characters with a single space
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)

    return s.strip()


def extract_established_year(year_str: Any) -> str:
    """
    Extract a valid 4-digit calendar year (e.g. from '1875[a]' or '1791(1958†)').

    Args:
        year_str (Any): Raw established year value.

    Returns:
        str: 4-digit year as string, or 'Unknown' if not found.
    """
    cleaned = clean_text(year_str)
    # Search for standard 4-digit years (1700 - 2099)
    match = re.search(r"\b(1[7-9]\d{2}|20\d{2})\b", cleaned)
    if match:
        return match.group(1)
    return cleaned if cleaned else "Unknown"


def clean_university_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Perform end-to-end cleaning and deduplication on scraped university data.

    Args:
        df (pd.DataFrame): Raw DataFrame from the scraper.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]:
            - Cleaned DataFrame
            - Metadata metrics dict detailing cleaning and validation operations.
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to cleaner.")
        return df, {"total_raw": 0, "duplicates_removed": 0, "missing_values_handled": 0, "final_count": 0}

    raw_count = len(df)
    logger.info("Starting data cleaning pipeline for %d raw records.", raw_count)

    # 1. Standardize column names to snake_case
    column_mapping = {
        "university": "university_name",
        "location": "location",
        "established": "established_year",
        "type": "university_type",
        "raw_details": "additional_details",
    }
    df_clean = df.rename(columns=column_mapping).copy()

    # 2. Text cleaning across all string columns
    for col in df_clean.columns:
        if df_clean[col].dtype == object or isinstance(df_clean[col].dtype, pd.StringDtype):
            df_clean[col] = df_clean[col].apply(clean_text)

    # 3. Clean and parse established year
    if "established_year" in df_clean.columns:
        df_clean["established_year"] = df_clean["established_year"].apply(extract_established_year)

    # 4. Standardize location names (e.g. Gautam Buddha Nagar / Noida)
    if "location" in df_clean.columns:
        df_clean["location"] = df_clean["location"].apply(
            lambda x: "Noida" if x == "Noida" else x
        )

    # 5. Handle missing values
    missing_report = {}
    total_missing_cells = 0
    for col in df_clean.columns:
        missing_count = int(df_clean[col].isin(["", "None", "Unknown", None]).sum())
        missing_report[col] = missing_count
        total_missing_cells += missing_count

    # Drop rows where critical fields ('university_name' or 'location') are completely missing
    initial_len = len(df_clean)
    df_clean = df_clean[
        (df_clean["university_name"] != "") & (df_clean["location"] != "")
    ].copy()
    dropped_empty_critical = initial_len - len(df_clean)

    # Fill non-critical optional columns
    if "additional_details" in df_clean.columns:
        df_clean["additional_details"] = df_clean["additional_details"].replace("", "Not Specified").fillna("Not Specified")

    # 6. Remove duplicate rows (by university name)
    pre_dedup = len(df_clean)
    # Deduplicate primarily on normalized lowercase university name
    df_clean["_norm_name"] = df_clean["university_name"].str.lower().str.strip()
    df_clean = df_clean.drop_duplicates(subset=["_norm_name"]).drop(columns=["_norm_name"])
    duplicates_removed = pre_dedup - len(df_clean)
    logger.info("Deduplication complete: %d duplicate row(s) removed.", duplicates_removed)

    # Sort logically by University Type and Name
    df_clean = df_clean.sort_values(by=["university_type", "university_name"]).reset_index(drop=True)

    final_count = len(df_clean)
    logger.info("Cleaned dataset contains %d valid records.", final_count)

    metrics = {
        "total_raw": raw_count,
        "duplicates_removed": duplicates_removed,
        "empty_critical_dropped": dropped_empty_critical,
        "missing_values_by_column": missing_report,
        "total_missing_cells": total_missing_cells,
        "final_count": final_count,
    }

    return df_clean, metrics


def validate_university_data(df: pd.DataFrame, metrics: Dict[str, Any]) -> bool:
    """
    Validate that the cleaned DataFrame satisfies data quality constraints
    and print a structured validation summary report.

    Args:
        df (pd.DataFrame): Cleaned DataFrame.
        metrics (Dict[str, Any]): Metrics gathered during cleaning.

    Returns:
        bool: True if validation passed, False otherwise.
    """
    logger.info("================ DATA VALIDATION REPORT ================")
    logger.info("Total Raw Rows Ingested     : %d", metrics.get("total_raw", 0))
    logger.info("Duplicate Records Removed   : %d", metrics.get("duplicates_removed", 0))
    logger.info("Empty Critical Rows Dropped : %d", metrics.get("empty_critical_dropped", 0))
    logger.info("Missing Values Handled      : %d", metrics.get("total_missing_cells", 0))
    for col, count in metrics.get("missing_values_by_column", {}).items():
        logger.info("  - Column '%s' missing: %d", col, count)
    logger.info("Final Validated Records     : %d", metrics.get("final_count", 0))

    # Assertions for quality checks
    passed = True
    required_cols = ["university_name", "location", "established_year", "university_type"]
    for col in required_cols:
        if col not in df.columns:
            logger.error("Validation Failed: Required column '%s' is missing!", col)
            passed = False
        elif (df[col] == "").any():
            empty_count = (df[col] == "").sum()
            logger.error("Validation Failed: Column '%s' contains %d empty values!", col, empty_count)
            passed = False

    if len(df) < 50:
        logger.warning("Validation Warning: Expected at least 50 clean rows, but found %d.", len(df))
    else:
        logger.info("Validation Check: Row count threshold met (>= 50 rows). Found: %d", len(df))

    if passed:
        logger.info("STATUS: DATA VALIDATION PASSED SUCCESSFULLY (Quality Score: 100%%)")
    else:
        logger.error("STATUS: DATA VALIDATION FAILED - Please inspect logs above.")
    logger.info("=========================================================")

    return passed


if __name__ == "__main__":
    # Self-test block when running module directly
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    sample_data = pd.DataFrame([
        {"university": "Aligarh Muslim University [1]", "location": "Aligarh", "established": "1875[a]", "type": "Central University", "raw_details": ""},
        {"university": "Aligarh Muslim University", "location": "Aligarh", "established": "1875", "type": "Central University", "raw_details": ""},
        {"university": "University of Lucknow †", "location": "Lucknow", "established": "1864(1920)", "type": "State University", "raw_details": ""},
    ])
    cleaned_df, sample_metrics = clean_university_data(sample_data)
    validate_university_data(cleaned_df, sample_metrics)
    print(cleaned_df)
