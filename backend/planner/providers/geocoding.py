import requests
import time
from abc import ABC, abstractmethod
from typing import Any

from .config import provider_config
from .models import GeocodedLocation
from .errors import handle_request_errors, GeocodingError
from .cache import ProviderCache


class GeocodingProvider(ABC):
    @abstractmethod
    def geocode(self, query: str) -> list[GeocodedLocation]:
        pass


class LocationIQProvider(GeocodingProvider):
    BASE_URL = "https://us1.locationiq.com/v1/search.php"

    def __init__(self, api_key: str | None = None, timeout: int = 10):
        self.api_key = api_key or provider_config.locationiq_api_key
        self.timeout = timeout
        self.cache = ProviderCache(prefix="geocoding")

    def geocode(self, query: str) -> list[GeocodedLocation]:
        if not query.strip():
            return []
            
        # Check cache first
        cached_result = self.cache.get(query)
        if cached_result is not None:
            return [GeocodedLocation(**item) for item in cached_result]

        # Call remote API
        results = self._fetch_remote(query)
        
        # Save to cache if we got results
        if results:
            self.cache.set(query, [r.model_dump() for r in results])
            
        return results

    @handle_request_errors("LocationIQ")
    def _fetch_remote(self, query: str) -> list[GeocodedLocation]:
        if not self.api_key:
            raise GeocodingError("LocationIQ API key is missing.", "LocationIQ")

        params = {
            "key": self.api_key,
            "q": query,
            "format": "json",
            "limit": 5,
        }

        # Handle strict 2 req/sec limit with a simple retry
        for attempt in range(2):
            response = requests.get(
                self.BASE_URL, 
                params=params, 
                timeout=self.timeout
            )
            
            if response.status_code == 429 and attempt == 0:
                time.sleep(0.6) # Wait for the 2 req/sec window to clear
                continue
                
            if response.status_code == 404:
                return []
                
            response.raise_for_status()
            break
            
        data = response.json()

        results = []
        for item in data:
            results.append(
                GeocodedLocation(
                    lat=float(item["lat"]),
                    lon=float(item["lon"]),
                    display_name=item["display_name"],
                    raw_response=item,
                )
            )
        return results

# Singleton instance for general use
geocoder = LocationIQProvider()
