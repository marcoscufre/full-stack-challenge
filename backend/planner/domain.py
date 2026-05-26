from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum


class EventType(StrEnum):
    OFF_DUTY = "off_duty"
    SLEEPER = "sleeper"
    DRIVING = "driving"
    ON_DUTY = "on_duty"


class StopType(StrEnum):
    ORIGIN = "origin"
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    BREAK = "break"
    FUEL = "fuel"
    REST = "rest"


@dataclass(slots=True, frozen=True)
class RouteLeg:
    name: str
    origin_label: str
    destination_label: str
    distance_miles: float
    duration_minutes: int
    geometry_coords: list[tuple[float, float]] | None = None


@dataclass(slots=True, frozen=True)
class RouteOverride:
    distance_miles: float
    duration_minutes: int


@dataclass(slots=True, frozen=True)
class MockRouteOverrides:
    current_to_pickup: RouteOverride | None = None
    pickup_to_dropoff: RouteOverride | None = None


@dataclass(slots=True, frozen=True)
class RouteSummaryData:
    total_distance_miles: float
    total_duration_hours: float
    total_driving_hours: float
    total_on_duty_hours: float
    total_rest_hours: float
    estimated_days: int


@dataclass(slots=True, frozen=True)
class PlannedStop:
    type: StopType
    label: str
    location: str
    sequence: int
    lat: float | None = None
    lon: float | None = None


@dataclass(slots=True, frozen=True)
class DutySegment:
    status: EventType
    label: str
    start_at: datetime
    end_at: datetime
    duration_minutes: int
    location: str
    notes: str | None = None
    lat: float | None = None
    lon: float | None = None


@dataclass(slots=True, frozen=True)
class PlannedActivity:
    status: EventType
    label: str
    location: str
    duration_minutes: int
    distance_miles: float = 0.0
    source_leg_name: str | None = None
    notes: str | None = None
    lat: float | None = None
    lon: float | None = None


@dataclass(slots=True, frozen=True)
class FuelStopPlan:
    location: str
    trigger_mile_marker: float
    duration_minutes: int
    notes: str | None = None


@dataclass(slots=True, frozen=True)
class RestBreakPlan:
    location: str
    reason: str
    duration_minutes: int
    status: EventType = EventType.OFF_DUTY


@dataclass(slots=True, frozen=True)
class DailyRecapData:
    off_duty_hours: float
    sleeper_hours: float
    driving_hours: float
    on_duty_not_driving_hours: float


@dataclass(slots=True, frozen=True)
class LogGridInterval:
    status: EventType
    row_index: int
    start_minute: int
    end_minute: int
    start_hour: float
    end_hour: float
    x_start: float
    x_end: float
    duration_minutes: int
    label: str


@dataclass(slots=True, frozen=True)
class LogGridTransition:
    minute: int
    hour: float
    from_status: EventType
    to_status: EventType
    x_position: float


@dataclass(slots=True, frozen=True)
class DailyLogGridData:
    intervals: list[LogGridInterval]
    transitions: list[LogGridTransition]
    total_minutes: int
    grid_start_hour: int = 0
    grid_end_hour: int = 24


@dataclass(slots=True, frozen=True)
class DailyLogData:
    day_index: int
    service_date: date
    remarks: list[str]
    recap: DailyRecapData
    segments: list[DutySegment]
    grid: DailyLogGridData | None = None


@dataclass(slots=True, frozen=True)
class TripPlanData:
    request_snapshot: dict[str, object]
    assumptions: list[str]
    route_legs: list[RouteLeg]
    route_stops: list[PlannedStop]
    timeline: list[DutySegment]
    daily_logs: list[DailyLogData]
    summary: RouteSummaryData
    warnings: list[str] = field(default_factory=list)
    fuel_stops: list[FuelStopPlan] = field(default_factory=list)
    rest_breaks: list[RestBreakPlan] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class HosPlanResult:
    timeline: list[DutySegment]
    warnings: list[str] = field(default_factory=list)
