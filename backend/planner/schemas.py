from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TripPlanRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    current_location: str = Field(min_length=2, max_length=255)
    pickup_location: str = Field(min_length=2, max_length=255)
    dropoff_location: str = Field(min_length=2, max_length=255)
    current_cycle_used_hours: float = Field(ge=0, le=70)
    trip_start_at: datetime | None = None

    @field_validator("current_location", "pickup_location", "dropoff_location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Location cannot be blank.")
        return value


class TripSummary(BaseModel):
    total_distance_miles: float
    total_duration_hours: float
    total_driving_hours: float
    total_on_duty_hours: float
    total_rest_hours: float
    estimated_days: int


class TimelineEvent(BaseModel):
    type: str
    label: str
    start_at: str
    end_at: str
    duration_minutes: int
    location: str
    notes: str | None = None


class RouteStop(BaseModel):
    type: str
    label: str
    location: str
    sequence: int


class DailyLogSheet(BaseModel):
    day_index: int
    date_label: str
    remarks: list[str]
    recap: dict[str, float]
    segments: list[dict[str, str | int | float]]


class TripPlanResponse(BaseModel):
    request: TripPlanRequest
    assumptions: list[str]
    summary: TripSummary
    route_stops: list[RouteStop]
    timeline: list[TimelineEvent]
    daily_logs: list[DailyLogSheet]
    warnings: list[str]
