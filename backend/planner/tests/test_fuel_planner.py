from backend.planner.domain import EventType, MockRouteOverrides, PlannedActivity, RouteOverride
from backend.planner.schemas import TripPlanRequest
from backend.planner.services import build_trip_plan_data
from backend.planner.services.fuel_planner import insert_fuel_stops


def test_fuel_planner_inserts_one_stop_after_one_thousand_miles():
    activities = [
        PlannedActivity(
            status=EventType.DRIVING,
            label="Long drive",
            location="Dallas, TX -> Denver, CO",
            duration_minutes=1200,
            distance_miles=1200,
            source_leg_name="leg-1",
        )
    ]

    result = insert_fuel_stops(activities)

    assert len(result.fuel_stops) == 1
    assert result.fuel_stops[0].trigger_mile_marker == 1000
    assert result.activities[1].label == "Fuel stop"
    assert result.activities[1].status == EventType.ON_DUTY


def test_fuel_planner_inserts_multiple_stops_for_very_long_trip():
    activities = [
        PlannedActivity(
            status=EventType.DRIVING,
            label="Very long drive",
            location="Los Angeles, CA -> Chicago, IL",
            duration_minutes=3000,
            distance_miles=2500,
            source_leg_name="leg-1",
        )
    ]

    result = insert_fuel_stops(activities)

    assert len(result.fuel_stops) == 2
    assert result.fuel_stops[0].trigger_mile_marker == 1000
    assert result.fuel_stops[1].trigger_mile_marker == 2000
    assert [activity.label for activity in result.activities].count("Fuel stop") == 2


def test_trip_planner_adds_fuel_stops_to_timeline_and_route_stops():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Phoenix, AZ",
        current_cycle_used_hours=0,
    )
    overrides = MockRouteOverrides(
        current_to_pickup=RouteOverride(distance_miles=1200.0, duration_minutes=1200),
        pickup_to_dropoff=RouteOverride(distance_miles=1100.0, duration_minutes=1080),
    )

    trip_data = build_trip_plan_data(payload, route_overrides=overrides)

    fuel_timeline_segments = [
        segment for segment in trip_data.timeline if segment.label == "Fuel stop"
    ]
    fuel_route_stops = [
        stop for stop in trip_data.route_stops if stop.type.value == "fuel"
    ]

    assert len(trip_data.fuel_stops) == 2
    assert len(fuel_timeline_segments) == 2
    assert len(fuel_route_stops) == 2
    assert all(segment.status == EventType.ON_DUTY for segment in fuel_timeline_segments)
    assert trip_data.summary.total_on_duty_hours >= 3.0
