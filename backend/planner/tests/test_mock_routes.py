from backend.planner.domain import MockRouteOverrides, RouteOverride
from backend.planner.mock_routes import resolve_mock_route_legs
from backend.planner.schemas import TripPlanRequest
from backend.planner.services import build_trip_plan_data


def test_mock_routes_return_two_normalized_route_legs():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=12,
    )

    route_legs = resolve_mock_route_legs(payload)

    assert len(route_legs) == 2
    assert route_legs[0].name == "current_to_pickup"
    assert route_legs[0].origin_label == "Dallas, TX"
    assert route_legs[0].destination_label == "Austin, TX"
    assert route_legs[1].name == "pickup_to_dropoff"
    assert route_legs[1].origin_label == "Austin, TX"
    assert route_legs[1].destination_label == "Houston, TX"
    assert route_legs[0].distance_miles >= 0
    assert route_legs[1].duration_minutes >= 0


def test_mock_routes_are_deterministic_for_same_input():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=12,
    )

    first = resolve_mock_route_legs(payload)
    second = resolve_mock_route_legs(payload)

    assert first == second


def test_mock_routes_accept_explicit_overrides():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=12,
    )
    overrides = MockRouteOverrides(
        current_to_pickup=RouteOverride(distance_miles=180.0, duration_minutes=210),
        pickup_to_dropoff=RouteOverride(distance_miles=165.0, duration_minutes=195),
    )

    route_legs = resolve_mock_route_legs(payload, overrides=overrides)

    assert route_legs[0].distance_miles == 180.0
    assert route_legs[0].duration_minutes == 210
    assert route_legs[1].distance_miles == 165.0
    assert route_legs[1].duration_minutes == 195


def test_trip_planner_runs_end_to_end_with_mock_route_overrides():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=12,
    )
    overrides = MockRouteOverrides(
        current_to_pickup=RouteOverride(distance_miles=180.0, duration_minutes=210),
        pickup_to_dropoff=RouteOverride(distance_miles=165.0, duration_minutes=195),
    )

    trip_data = build_trip_plan_data(payload, route_overrides=overrides)

    assert len(trip_data.route_legs) == 2
    assert trip_data.summary.total_distance_miles == 345.0
    assert trip_data.timeline[0].label == "Drive to pickup"
    assert trip_data.timeline[0].duration_minutes == 210
    assert trip_data.timeline[2].duration_minutes == 195
    assert trip_data.daily_logs[0].recap.driving_hours == 6.75
