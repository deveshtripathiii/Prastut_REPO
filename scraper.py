"""
scraper.py
==========
Module to scrape university listings from Wikipedia using requests,
BeautifulSoup, and pandas. Adheres to ethical scraping standards with
proper User-Agent headers and polite delay handling.
"""

import logging
import time
from typing import Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_universities_in_Uttar_Pradesh"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 "
    "(Research Data Analyst Project; UP Universities Scraper)"
)


def fetch_html(url: str, user_agent: str = DEFAULT_USER_AGENT, timeout: int = 15) -> Optional[str]:
    """
    Fetch the raw HTML content from the specified URL using requests.

    Args:
        url (str): Target web page URL.
        user_agent (str): User-Agent string to send in request headers.
        timeout (int): Request timeout in seconds.

    Returns:
        Optional[str]: HTML string if successful, None otherwise.
    """
    headers = {"User-Agent": user_agent}
    try:
        logger.info("Sending GET request to %s", url)
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        logger.info("Successfully fetched page content (HTTP %d, %d bytes)", response.status_code, len(response.text))
        return response.text
    except requests.exceptions.HTTPError as http_err:
        logger.error("HTTP error occurred while fetching %s: %s", url, http_err)
    except requests.exceptions.ConnectionError as conn_err:
        logger.error("Connection error occurred while fetching %s: %s", url, conn_err)
    except requests.exceptions.Timeout as timeout_err:
        logger.error("Timeout reached while fetching %s: %s", url, timeout_err)
    except requests.exceptions.RequestException as req_err:
        logger.error("Unexpected network error while fetching %s: %s", url, req_err)
    return None


def parse_university_tables(html_content: str) -> pd.DataFrame:
    """
    Parse university tables from the Wikipedia HTML content.
    Extracts Central, State, Private, and Deemed universities.

    Args:
        html_content (str): Raw HTML string of the Wikipedia page.

    Returns:
        pd.DataFrame: Raw DataFrame containing extracted university rows.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table", class_="wikitable")

    if not tables:
        logger.warning("No tables with class 'wikitable' found on the page.")
        return pd.DataFrame()

    logger.info("Found %d wikitable(s) on the page.", len(tables))

    # Mapping table indices to university types based on page structure:
    # Table 0: Summary count table
    # Table 1: Central Universities
    # Table 2: State Universities
    # Table 3: Private Universities
    # Table 4: Deemed Universities
    table_type_mapping = {
        1: "Central University",
        2: "State University",
        3: "Private University",
        4: "Deemed University",
    }

    records = []

    for table_idx, uni_type in table_type_mapping.items():
        if table_idx >= len(tables):
            logger.warning("Table index %d out of range (total tables: %d)", table_idx, len(tables))
            continue

        table = tables[table_idx]
        rows = table.find_all("tr")
        if not rows:
            continue

        extracted_from_table = 0
        for tr in rows[1:]:  # Skip table header row
            cells = tr.find_all(["td", "th"])
            if len(cells) < 3:
                continue

            # Core columns present in all 4 university tables:
            # Col 0: University Name
            # Col 1: Location / City
            # Col 2: Established Year
            uni_name = cells[0].get_text(strip=True)
            location = cells[1].get_text(strip=True)
            established = cells[2].get_text(strip=True)

            # Optional specialization / notes if additional columns exist
            specialization = ""
            if len(cells) >= 4:
                # In Table 1, col 3 is University status, col 4 is Enrolled students
                extra_text = " ".join(c.get_text(strip=True) for c in cells[3:])
                specialization = extra_text

            records.append({
                "university": uni_name,
                "location": location,
                "established": established,
                "type": uni_type,
                "raw_details": specialization,
            })
            extracted_from_table += 1

        logger.info("Extracted %d %s entries from table %d.", extracted_from_table, uni_type, table_idx)

    df_raw = pd.DataFrame(records)
    logger.info("Total raw records extracted across all tables: %d", len(df_raw))
    return df_raw


def scrape_up_universities(url: str = DEFAULT_WIKI_URL, delay: float = 1.0) -> pd.DataFrame:
    """
    High-level scraper pipeline function that fetches and parses university data.

    Args:
        url (str): Wikipedia URL.
        delay (float): Politeness delay in seconds.

    Returns:
        pd.DataFrame: Scraped raw DataFrame.
    """
    logger.info("Starting scrape pipeline for URL: %s", url)
    if delay > 0:
        logger.info("Polite delay of %.2f second(s) before network request...", delay)
        time.sleep(delay)

    html = fetch_html(url)
    if not html:
        logger.error("Failed to retrieve HTML content. Returning empty DataFrame.")
        return pd.DataFrame()

    df = parse_university_tables(html)
    return df


if __name__ == "__main__":
    # Self-test block when running module directly
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    test_df = scrape_up_universities()
    print(f"Scraped {len(test_df)} raw records.")
    if not test_df.empty:
        print(test_df.head(5))
