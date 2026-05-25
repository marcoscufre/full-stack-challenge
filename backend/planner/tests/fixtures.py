from datetime import datetime, timedelta, UTC
from dataclasses import dataclass
from ..schemas import TripPlanRequest
from ..domain import MockRouteOverrides, RouteOverride

@dataclass(frozen=True)
class TripScenario:
    name: str
    description: str
    request: TripPlanRequest
    overrides: MockRouteOverrides

def get_same_day_scenario() -> TripScenario:
    """A short trip that starts and ends on the same day without requiring breaks."""
    start_at = datetime(2026, 6, 1, 8, 0, tzinfo=UTC)
    return TripScenario(
        name="same_day_trip",
        description="Short trip, no breaks required",
        request=TripPlanRequest(
            current_location="Miami, FL",
            pickup_location="Fort Lauderdale, FL",
            dropoff_location="West Palm Beach, FL",
            current_cycle_used_hours=0.0,
            trip_start_at=start_at,
        ),
        overrides=MockRouteOverrides(
            current_to_pickup=RouteOverride(distance_miles=30, duration_minutes=45),
            pickup_to_dropoff=RouteOverride(distance_miles=50, duration_minutes=60),
        )
    )

def get_overnight_scenario() -> TripScenario:
    """A trip that starts in the afternoon and crosses midnight, requiring a 10-hour reset."""
    start_at = datetime(2026, 6, 1, 16, 0, tzinfo=UTC)
    return TripScenario(
        name="overnight_trip",
        description="Crosses midnight, requires 10h reset",
        request=TripPlanRequest(
            current_location="Atlanta, GA",
            pickup_location="Birmingham, AL",
            dropoff_location="New Orleans, LA",
            current_cycle_used_hours=5.0,
            trip_start_at=start_at,
        ),
        overrides=MockRouteOverrides(
            current_to_pickup=RouteOverride(distance_miles=150, duration_minutes=180),
            pickup_to_dropoff=RouteOverride(distance_miles=350, duration_minutes=420),
        )
    )

def get_multi_day_scenario() -> TripScenario:
    """A long trip spanning 3+ days with multiple resets and fuel stops."""
    start_at = datetime(2026, 6, 1, 7, 0, tzinfo=UTC)
    return TripScenario(
        name="multi_day_trip",
        description="3-day trip with multiple resets",
        request=TripPlanRequest(
            current_location="New York, NY",
            pickup_location="Chicago, IL",
            dropoff_location="Los Angeles, CA",
            current_cycle_used_hours=10.0,
            trip_start_at=start_at,
        ),
        overrides=MockRouteOverrides(
            current_to_pickup=RouteOverride(distance_miles=800, duration_minutes=900),
            pickup_to_dropoff=RouteOverride(distance_miles=2100, duration_minutes=2400),
        )
    )

def get_break_triggering_scenario() -> TripScenario:
    """A trip where a single leg exceeds 8 hours of driving, forcing a 30-min break."""
    start_at = datetime(2026, 6, 1, 6, 0, tzinfo=UTC)
    return TripScenario(
        name="break_triggering_trip",
        description="Forces a 30-minute break due to 8h driving rule",
        request=TripPlanRequest(
            current_location="Houston, TX",
            pickup_location="El Paso, TX",
            dropoff_location="Phoenix, AZ",
            current_cycle_used_hours=0.0,
            trip_start_at=start_at,
        ),
        overrides=MockRouteOverrides(
            current_to_pickup=RouteOverride(distance_miles=750, duration_minutes=540), # 9 hours
            pickup_to_dropoff=RouteOverride(distance_miles=400, duration_minutes=360),
        )
    )

def get_fuel_stop_triggering_scenario() -> TripScenario:
    """A trip that exceeds 1000 miles, forcing at least one fuel stop."""
    start_at = datetime(2026, 6, 1, 8, 0, tzinfo=UTC)
    return TripScenario(
        name="fuel_stop_triggering_trip",
        description="Forces a fuel stop (> 1000 miles)",
        request=TripPlanRequest(
            current_location="Seattle, WA",
            pickup_location="Portland, OR",
            dropoff_location="San Francisco, CA",
            current_cycle_used_hours=0.0,
            trip_start_at=start_at,
        ),
        overrides=MockRouteOverrides(
            current_to_pickup=RouteOverride(distance_miles=180, duration_minutes=200),
            pickup_to_dropoff=RouteOverride(distance_miles=1100, duration_minutes=1200),
        )
    )

SCENARIOS = {
    "same_day": get_same_day_scenario,
    "overnight": get_overnight_scenario,
    "multi_day": get_multi_day_scenario,
    "break_triggering": get_break_triggering_scenario,
    "fuel_stop_triggering": get_fuel_stop_triggering_scenario,
}
