from datetime import UTC, datetime

from backend.planner.domain import MockRouteOverrides, RouteOverride, StopType
from backend.planner.schemas import TripPlanRequest
from backend.planner.services import build_trip_plan, build_trip_plan_data, planner_orchestrator
from .fixtures import SCENARIOS


def test_orchestrator_builds_complete_trip_plan_data():
    scenario = SCENARIOS["overnight"]()
    
    trip_data = planner_orchestrator.plan_data(scenario.request, route_overrides=scenario.overrides)

    assert len(trip_data.route_legs) == 2
    assert len(trip_data.timeline) > 0
    assert len(trip_data.daily_logs) >= 2
    assert trip_data.summary.estimated_days == len(trip_data.daily_logs)
    assert trip_data.request_snapshot["current_location"] == scenario.request.current_location


def test_orchestrator_builds_complete_trip_plan_response():
    scenario = SCENARIOS["same_day"]()

    response = build_trip_plan(scenario.request, route_overrides=scenario.overrides)

    assert response.request.current_location == scenario.request.current_location
    assert response.summary.total_distance_miles == 80.0
    assert len(response.route_stops) >= 3
    assert len(response.timeline) > 0
    assert len(response.daily_logs) == 1


def test_multi_day_trip_planning_with_scenarios():
    scenario = SCENARIOS["multi_day"]()
    response = build_trip_plan(scenario.request, route_overrides=scenario.overrides)

    assert len(response.daily_logs) >= 3
    assert response.summary.estimated_days >= 3
    assert any(stop.type == StopType.FUEL for stop in response.route_stops)


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
