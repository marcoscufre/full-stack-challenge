import requests
from abc import ABC, abstractmethod
from typing import Any
from math import radians, cos, sin, asin, sqrt

from .config import provider_config
from .models import ExternalRouteLeg, RouteGeometry
from .errors import handle_request_errors, RoutingError
from .cache import ProviderCache


class RoutingProvider(ABC):
    @abstractmethod
    def get_directions(
        self, 
        start_coords: tuple[float, float], 
        end_coords: tuple[float, float]
    ) -> ExternalRouteLeg:
        pass


class OpenRouteServiceProvider(RoutingProvider):
    # Base profiles
    TRUCK_PROFILE = "driving-hgv"
    CAR_PROFILE = "driving-car"
    
    # NEW 2026 HeiGIT URL STRUCTURE
    BASE_URL_TEMPLATE = "https://api.heigit.org/openrouteservice/v2/directions/{profile}/geojson"

    def __init__(self, api_key: str | None = None, timeout: int = 20):
        self.api_key = (api_key or provider_config.openroutes_api_key or "").strip()
        self.timeout = timeout
        self.cache = ProviderCache(prefix="routing")

    def get_directions(
        self, 
        start_coords: tuple[float, float], 
        end_coords: tuple[float, float]
    ) -> ExternalRouteLeg:
        query_data = {"start": start_coords, "end": end_coords}
        
        cached_result = self.cache.get(query_data)
        if cached_result is not None:
            return ExternalRouteLeg(**cached_result)

        if not self.api_key:
            print("OpenRouteService API key is missing. Using simulated fallback.")
            leg = self._generate_simulated_leg(start_coords, end_coords)
            self.cache.set(query_data, leg.model_dump())
            return leg

        # 1. Try Truck Profile
        try:
            print(f"DEBUG: Attempting HGV routing for {start_coords} to {end_coords}")
            leg = self._fetch_remote(start_coords, end_coords, profile=self.TRUCK_PROFILE)
            print("DEBUG: HGV routing successful.")
        except Exception as e:
            # 2. Try Car Profile as secondary
            print(f"DEBUG: HGV routing failed: {str(e)}. Attempting Car profile fallback...")
            try:
                leg = self._fetch_remote(start_coords, end_coords, profile=self.CAR_PROFILE)
                print("DEBUG: Car profile fallback successful.")
            except Exception as car_e:
                print(f"DEBUG: Car profile also failed: {str(car_e)}")
                
                # ULTIMATE FALLBACK: If both fail, don't crash, simulate.
                print("WARNING: All ORS profiles failed. Using simulated fallback to keep app alive.")
                leg = self._generate_simulated_leg(start_coords, end_coords)
        
        self.cache.set(query_data, leg.model_dump())
        return leg

    def _generate_simulated_leg(self, start: tuple[float, float], end: tuple[float, float]) -> ExternalRouteLeg:
        """Calculates distance using Haversine formula and creates a straight-line geometry."""
        lat1, lon1, lat2, lon2 = map(radians, [start[0], start[1], end[0], end[1]])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # 3956 is radius of Earth in miles. 1.2 is winding factor for roads.
        miles = 3956 * c * 1.2 
        
        duration = (miles / 55) * 60 # Assume 55mph average
        
        return ExternalRouteLeg(
            distance_miles=round(miles, 2),
            duration_minutes=int(duration),
            geometry=RouteGeometry(
                coordinates=[[start[1], start[0]], [end[1], end[0]]]
            ),
            raw_response={"simulated": True, "warning": "External API keys disallowed or unavailable."}
        )

    @handle_request_errors("OpenRouteService")
    def _fetch_remote(
        self, 
        start_coords: tuple[float, float], 
        end_coords: tuple[float, float],
        profile: str
    ) -> ExternalRouteLeg:
        if not self.api_key:
            raise RoutingError("OpenRouteService API key is missing.", "OpenRouteService")

        url = self.BASE_URL_TEMPLATE.format(profile=profile)
        
        # We'll use both methods as some HeiGIT proxies are picky in 2026
        params = {"api_key": self.api_key}
        
        coordinates = [
            [start_coords[1], start_coords[0]],
            [end_coords[1], end_coords[0]]
        ]

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, application/geo+json"
        }
        
        body = {
            "coordinates": coordinates
        }

        print(f"DEBUG: POST {url} (Profile: {profile})")

        response = requests.post(
            url, 
            params=params,
            json=body, 
            headers=headers, 
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            print(f"DEBUG: ORS Failure - Status: {response.status_code}")
            print(f"DEBUG: ORS Failure - Body: {response.text}")
            
        response.raise_for_status()
        data = response.json()

        try:
            feature = data["features"][0]
            summary = feature["properties"]["summary"]
            geometry_data = feature["geometry"]

            # ORS returns distance in meters by default
            distance_meters = summary["distance"]
            distance_miles = distance_meters * 0.000621371

            return ExternalRouteLeg(
                distance_miles=distance_miles,
                duration_minutes=summary["duration"] / 60.0,
                geometry=RouteGeometry(
                    coordinates=geometry_data["coordinates"]
                ),
                raw_response=data,
            )
        except (KeyError, IndexError) as e:
            raise RoutingError(f"Unexpected response format from ORS: {str(e)}", "OpenRouteService")


router = OpenRouteServiceProvider()
