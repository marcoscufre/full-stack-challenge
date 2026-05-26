import requests
from abc import ABC, abstractmethod
from typing import Any

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
            # 2. Fallback to Car Profile if Truck fails (403 Forbidden or 404 Not Found)
            # This ensures the application works even if the HGV quota is hit or restricted
            print(f"HGV routing failed ({e}), falling back to car profile.")
            try:
                leg = self._fetch_remote(start_coords, end_coords, profile=self.CAR_PROFILE)
                if leg.raw_response:
                    leg.raw_response["routing_warning"] = "Truck-specific routing was unavailable. Fell back to car profile."
            except Exception as car_e:
                raise RoutingError(f"Routing failed on all profiles. Primary error: {str(e)}", "OpenRouteService")
        
        self.cache.set(query_data, leg.model_dump())
        return leg

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
            "radiuses": [-1, -1],  # Snap to nearest road regardless of distance
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
