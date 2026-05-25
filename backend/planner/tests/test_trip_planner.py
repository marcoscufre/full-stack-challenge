from datetime import UTC, datetime

from backend.planner.domain import MockRouteOverrides, RouteOverride
from backend.planner.schemas import TripPlanRequest
from backend.planner.services import build_trip_plan, build_trip_plan_data, planner_orchestrator


def test_orchestrator_builds_complete_trip_plan_data():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Phoenix, AZ",
        current_cycle_used_hours=0,
        trip_start_at=datetime(2026, 5, 25, 6, 0, tzinfo=UTC),
    )
    overrides = MockRouteOverrides(
        current_to_pickup=RouteOverride(distance_miles=600.0, duration_minutes=600),
        pickup_to_dropoff=RouteOverride(distance_miles=900.0, duration_minutes=900),
    )

    trip_data = planner_orchestrator.plan_data(payload, route_overrides=overrides)

    assert len(trip_data.route_legs) == 2
    assert len(trip_data.timeline) > 0
    assert len(trip_data.daily_logs) >= 2
    assert trip_data.summary.estimated_days == len(trip_data.daily_logs)
    assert trip_data.request_snapshot["current_location"] == "Dallas, TX"


def test_orchestrator_builds_complete_trip_plan_response():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=12,
        trip_start_at=datetime(2026, 5, 25, 10, 0, tzinfo=UTC),
    )
    overrides = MockRouteOverrides(
        current_to_pickup=RouteOverride(distance_miles=180.0, duration_minutes=210),
        pickup_to_dropoff=RouteOverride(distance_miles=165.0, duration_minutes=195),
    )

    response = build_trip_plan(payload, route_overrides=overrides)

    assert response.request.current_location == "Dallas, TX"
    assert response.summary.total_distance_miles == 345.0
    assert len(response.route_stops) >= 3
    assert len(response.timeline) > 0
    assert len(response.daily_logs) >= 1


def test_public_build_trip_plan_data_uses_same_orchestrator_pipeline():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=0,
    )

    direct = planner_orchestrator.plan_data(payload)
    public = build_trip_plan_data(payload)

    assert direct.summary.total_distance_miles == public.summary.total_distance_miles
    assert len(direct.timeline) == len(public.timeline)
