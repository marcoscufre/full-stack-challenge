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
    
    BASE_URL_TEMPLATE = "https://api.openrouteservice.org/v2/directions/{profile}/geojson"

    def __init__(self, api_key: str | None = None, timeout: int = 15):
        self.api_key = api_key or provider_config.openroutes_api_key
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

        # 1. Try Truck Profile First
        try:
            leg = self._fetch_remote(start_coords, end_coords, profile=self.TRUCK_PROFILE)
        except Exception as e:
            # 2. Try Car Profile Second
            print(f"HGV routing failed ({e}), trying car profile.")
            try:
                leg = self._fetch_remote(start_coords, end_coords, profile=self.CAR_PROFILE)
            except Exception as car_e:
                # 3. EMERGENCY FALLBACK: Simulated Routing
                # This ensures the HOS engine works even if external API keys are blocked/invalid
                print(f"External routing totally failed ({car_e}). Using simulated fallback.")
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
            raw_response={"simulated": True, "warning": "External API keys unavailable."}
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
        coordinates = [
            [start_coords[1], start_coords[0]],
            [end_coords[1], end_coords[0]]
        ]

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        
        body = {
            "coordinates": coordinates,
            "units": "mi",
            "radiuses": [-1, -1],
        }

        response = requests.post(
            url, 
            json=body, 
            headers=headers, 
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        try:
            feature = data["features"][0]
            summary = feature["properties"]["summary"]
            geometry_data = feature["geometry"]

            return ExternalRouteLeg(
                distance_miles=summary["distance"],
                duration_minutes=summary["duration"] / 60.0,
                geometry=RouteGeometry(
                    coordinates=geometry_data["coordinates"]
                ),
                raw_response=data,
            )
        except (KeyError, IndexError) as e:
            raise RoutingError(f"Unexpected response format from ORS: {str(e)}", "OpenRouteService")


router = OpenRouteServiceProvider()
