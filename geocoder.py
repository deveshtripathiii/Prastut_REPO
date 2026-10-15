"""
geocoder.py
===========
Geocoding and spatial distance computation module.
Uses geopy with OpenStreetMap's Nominatim API, implements persistent local
file caching, respects the 1-request-per-second rate limit, and calculates
great-circle distances to Greater Noida using the Haversine formula.
"""

import json
import logging
import math
import os
import ssl
import time
from typing import Dict, Optional, Tuple
import certifi
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
import pandas as pd

logger = logging.getLogger(__name__)

# Reference location: Greater Noida, Uttar Pradesh, India
GREATER_NOIDA_LAT = 28.4744
GREATER_NOIDA_LON = 77.5040

DEFAULT_CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache", "geocode_cache.json")


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two geographical points
    on Earth using the Haversine formula.

    Args:
        lat1 (float): Latitude of point 1 in decimal degrees.
        lon1 (float): Longitude of point 1 in decimal degrees.
        lat2 (float): Latitude of point 2 in decimal degrees.
        lon2 (float): Longitude of point 2 in decimal degrees.

    Returns:
        float: Distance in kilometers, rounded to 2 decimal places.
    """
    earth_radius_km = 6371.0

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance_km = earth_radius_km * c

    return round(distance_km, 2)


class UniversityGeocoder:
    """
    Geocoder client for university locations with built-in rate-limiting,
    persistent JSON caching, and SSL certificate verification.
    """

    def __init__(
        self,
        cache_path: str = DEFAULT_CACHE_FILE,
        user_agent: str = "up_universities_research_extractor_geopy",
        rate_limit_delay: float = 1.05,
    ):
        """
        Initialize the geocoder with cache and geolocator.

        Args:
            cache_path (str): Filepath to persistent JSON cache.
            user_agent (str): Identifying User-Agent for Nominatim.
            rate_limit_delay (float): Delay in seconds between live requests (minimum 1.0s).
        """
        self.cache_path = cache_path
        self.rate_limit_delay = max(rate_limit_delay, 1.0)
        self.cache: Dict[str, Dict[str, Optional[float]]] = {}
        self._load_cache()

        # Build SSL context with certifi to avoid macOS SSL verification issues
        try:
            ctx = ssl.create_default_context(cafile=certifi.where())
            self.geolocator = Nominatim(user_agent=user_agent, ssl_context=ctx)
        except Exception as e:
            logger.warning("Could not set custom certifi SSL context (%s). Falling back to default.", e)
            self.geolocator = Nominatim(user_agent=user_agent)

    def _load_cache(self) -> None:
        """Load cached coordinates from disk if file exists."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
                logger.info("Loaded %d cached location coordinates from %s", len(self.cache), self.cache_path)
            except Exception as e:
                logger.warning("Failed to read cache file (%s). Starting with empty cache.", e)
                self.cache = {}
        else:
            self.cache = {}

    def _save_cache(self) -> None:
        """Persist current coordinates cache to disk."""
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.debug("Persisted %d locations to geocode cache.", len(self.cache))
        except Exception as e:
            logger.error("Failed to persist geocode cache to %s: %s", self.cache_path, e)

    def geocode_location(self, location_name: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Geocode a city or location name to (latitude, longitude).
        Checks local cache first. If cache miss, calls Nominatim respecting rate limits.

        Args:
            location_name (str): City or district name.

        Returns:
            Tuple[Optional[float], Optional[float]]: (latitude, longitude) or (None, None).
        """
        norm_key = location_name.strip()
        if not norm_key:
            return None, None

        # 1. Check in-memory / persistent cache
        if norm_key in self.cache:
            entry = self.cache[norm_key]
            logger.debug("Cache hit for location: '%s' -> (%s, %s)", norm_key, entry.get("lat"), entry.get("lon"))
            return entry.get("lat"), entry.get("lon")

        # 2. Query Nominatim with polite delay
        logger.info("Cache miss for '%s'. Geocoding via Nominatim API...", norm_key)
        queries = [
            f"{norm_key}, Uttar Pradesh, India",
            f"{norm_key}, India",
        ]

        lat, lon = None, None
        for query in queries:
            try:
                time.sleep(self.rate_limit_delay)  # Respect OpenStreetMap 1 req/sec policy
                location_result = self.geolocator.geocode(query, timeout=10)
                if location_result:
                    lat = round(location_result.latitude, 6)
                    lon = round(location_result.longitude, 6)
                    logger.info("Resolved '%s' -> Lat: %.4f, Lon: %.4f", norm_key, lat, lon)
                    break
            except (GeocoderTimedOut, GeocoderServiceError) as geo_err:
                logger.warning("Geocoding service error for query '%s': %s", query, geo_err)
            except Exception as err:
                logger.error("Unexpected error geocoding '%s': %s", query, err)

        # 3. Store in cache (even if None, to prevent repetitive failed API calls)
        self.cache[norm_key] = {"lat": lat, "lon": lon}
        self._save_cache()
        return lat, lon

    def enrich_dataframe_with_geodata(
        self,
        df: pd.DataFrame,
        location_col: str = "location",
        ref_lat: float = GREATER_NOIDA_LAT,
        ref_lon: float = GREATER_NOIDA_LON,
    ) -> pd.DataFrame:
        """
        Enrich a university DataFrame with latitude, longitude, and Haversine
        distance from Greater Noida in kilometers.

        Args:
            df (pd.DataFrame): Input DataFrame containing university records.
            location_col (str): Column name containing location names.
            ref_lat (float): Reference latitude (Greater Noida).
            ref_lon (float): Reference longitude (Greater Noida).

        Returns:
            pd.DataFrame: Enriched DataFrame with new geospatial columns.
        """
        if df.empty or location_col not in df.columns:
            logger.warning("Cannot enrich DataFrame: empty or '%s' column missing.", location_col)
            return df

        df_enriched = df.copy()

        # Find unique locations to minimize geocoding requests
        unique_locations = df_enriched[location_col].unique()
        logger.info("Geocoding %d unique locations across %d rows...", len(unique_locations), len(df_enriched))

        loc_coord_map: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
        for loc in unique_locations:
            lat, lon = self.geocode_location(loc)
            loc_coord_map[loc] = (lat, lon)

        # Map coordinates back to full DataFrame
        df_enriched["latitude"] = df_enriched[location_col].map(lambda x: loc_coord_map.get(x, (None, None))[0])
        df_enriched["longitude"] = df_enriched[location_col].map(lambda x: loc_coord_map.get(x, (None, None))[1])

        # Compute Haversine distance from Greater Noida
        def compute_dist(row):
            lat = row.get("latitude")
            lon = row.get("longitude")
            if pd.notna(lat) and pd.notna(lon):
                return haversine_distance(lat, lon, ref_lat, ref_lon)
            return None

        df_enriched["distance_from_greater_noida_km"] = df_enriched.apply(compute_dist, axis=1)

        logger.info("Geospatial enrichment complete. Added latitude, longitude, and distance_from_greater_noida_km.")
        return df_enriched


if __name__ == "__main__":
    # Self-test block when running module directly
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    geocoder = UniversityGeocoder()
    test_locations = ["Lucknow", "Greater Noida", "Varanasi"]
    for loc_name in test_locations:
        lat_res, lon_res = geocoder.geocode_location(loc_name)
        if lat_res and lon_res:
            dist = haversine_distance(lat_res, lon_res, GREATER_NOIDA_LAT, GREATER_NOIDA_LON)
            print(f"{loc_name:15}: ({lat_res:.4f}, {lon_res:.4f}) -> {dist:.2f} km to Greater Noida")
