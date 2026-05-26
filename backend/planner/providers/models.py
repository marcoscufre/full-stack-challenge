from dataclasses import dataclass
from pydantic import BaseModel, Field

class GeocodedLocation(BaseModel):
    lat: float
    lon: float
    display_name: str
    raw_response: dict = Field(default_factory=dict, exclude=True)

class RouteGeometry(BaseModel):
    coordinates: list[tuple[float, float]]  # [lon, lat] pairs as common in GeoJSON
    polyline: str | None = None

class ExternalRouteLeg(BaseModel):
    distance_miles: float
    duration_minutes: float
    geometry: RouteGeometry | None = None
    raw_response: dict = Field(default_factory=dict, exclude=True)

class ProviderErrorData(BaseModel):
    code: str
    message: str
    provider_name: str
