from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .domain import EventType, StopType

from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_JSON = "invalid_json"
    VALIDATION_ERROR = "validation_error"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    PLANNER_EXECUTION_ERROR = "planner_execution_error"
    INVALID_CYCLE_USAGE = "invalid_cycle_usage"
    IMPOSSIBLE_TRIP = "impossible_trip"
    MOCK_ROUTE_ERROR = "mock_route_error"


class TripPlanRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

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
    model_config = ConfigDict(extra="forbid")

    total_distance_miles: float = Field(ge=0)
    total_duration_hours: float = Field(ge=0)
    total_driving_hours: float = Field(ge=0)
    total_on_duty_hours: float = Field(ge=0)
    total_rest_hours: float = Field(ge=0)
    estimated_days: int = Field(ge=1)


class TimelineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: EventType
    label: str = Field(min_length=1, max_length=120)
    start_at: datetime
    end_at: datetime
    duration_minutes: int = Field(ge=0)
    location: str = Field(min_length=1, max_length=255)
    notes: str | None = Field(default=None, max_length=500)
    lat: float | None = None
    lon: float | None = None


class RouteStop(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: StopType
    label: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=255)
    sequence: int = Field(ge=1)
    lat: float | None = None
    lon: float | None = None


class DailyLogSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EventType
    start_at: datetime
    end_at: datetime
    duration_minutes: int = Field(ge=0)


class DailyLogRecap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    off_duty_hours: float = Field(ge=0)
    sleeper_hours: float = Field(ge=0)
    driving_hours: float = Field(ge=0)
    on_duty_not_driving_hours: float = Field(ge=0)


class DailyLogGridInterval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EventType
    row_index: int = Field(ge=0, le=3)
    start_minute: int = Field(ge=0, le=1440)
    end_minute: int = Field(ge=0, le=1440)
    start_hour: float = Field(ge=0, le=24)
    end_hour: float = Field(ge=0, le=24)
    x_start: float = Field(ge=0, le=1)
    x_end: float = Field(ge=0, le=1)
    duration_minutes: int = Field(ge=0)
    label: str = Field(min_length=1, max_length=120)


class DailyLogGridTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minute: int = Field(ge=0, le=1440)
    hour: float = Field(ge=0, le=24)
    from_status: EventType
    to_status: EventType
    x_position: float = Field(ge=0, le=1)


class DailyLogGrid(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intervals: list[DailyLogGridInterval]
    transitions: list[DailyLogGridTransition]
    total_minutes: int = Field(ge=0, le=1440)
    grid_start_hour: int = Field(ge=0, le=24)
    grid_end_hour: int = Field(ge=0, le=24)


class DailyLogSheet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day_index: int = Field(ge=1)
    date_label: str = Field(min_length=1, max_length=20)
    remarks: list[str]
    recap: DailyLogRecap
    segments: list[DailyLogSegment]
    grid: DailyLogGrid


class TripPlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: TripPlanRequest
    assumptions: list[str]
    summary: TripSummary
    route_stops: list[RouteStop]
    timeline: list[TimelineEvent]
    daily_logs: list[DailyLogSheet]
    warnings: list[str]
    route_geometry: list[tuple[float, float]] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    message: str
    type: str


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ErrorCode
    detail: str
    errors: list[ValidationIssue] = Field(default_factory=list)
