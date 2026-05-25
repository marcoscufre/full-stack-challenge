from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .domain import EventType, StopType

from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_JSON = "invalid_json"
    VALIDATION_ERROR = "validation_error"
    METHOD_NOT_ALLOWED = "method_not_allowed"


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


class RouteStop(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: StopType
    label: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=255)
    sequence: int = Field(ge=1)


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


class DailyLogSheet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day_index: int = Field(ge=1)
    date_label: str = Field(min_length=1, max_length=20)
    remarks: list[str]
    recap: DailyLogRecap
    segments: list[DailyLogSegment]


class TripPlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: TripPlanRequest
    assumptions: list[str]
    summary: TripSummary
    route_stops: list[RouteStop]
    timeline: list[TimelineEvent]
    daily_logs: list[DailyLogSheet]
    warnings: list[str]


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
