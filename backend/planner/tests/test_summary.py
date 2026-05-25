from datetime import UTC, datetime

from backend.planner.domain import MockRouteOverrides, RouteOverride
from backend.planner.schemas import TripPlanRequest
from backend.planner.services import build_trip_plan_data
from backend.planner.services.summary import build_trip_summary


def test_summary_matches_timeline_totals():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=0,
        trip_start_at=datetime(2026, 5, 25, 6, 0, tzinfo=UTC),
    )
    overrides = MockRouteOverrides(
        current_to_pickup=RouteOverride(distance_miles=180.0, duration_minutes=210),
        pickup_to_dropoff=RouteOverride(distance_miles=165.0, duration_minutes=195),
    )

    trip_data = build_trip_plan_data(payload, route_overrides=overrides)
    summary = build_trip_summary(
        route_legs=trip_data.route_legs,
        timeline=trip_data.timeline,
        daily_logs=trip_data.daily_logs,
    )

    assert summary.total_distance_miles == 345.0
    assert summary.total_duration_hours == sum(
        segment.duration_minutes for segment in trip_data.timeline
    ) / 60
    assert summary.total_driving_hours == sum(
        segment.duration_minutes
        for segment in trip_data.timeline
        if segment.status.value == "driving"
    ) / 60
    assert summary.total_on_duty_hours == sum(
        segment.duration_minutes
        for segment in trip_data.timeline
        if segment.status.value == "on_duty"
    ) / 60


def test_summary_estimated_days_matches_daily_logs_count():
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

    trip_data = build_trip_plan_data(payload, route_overrides=overrides)

    assert trip_data.summary.estimated_days == len(trip_data.daily_logs)


def test_summary_reconciles_exactly_with_daily_logs():
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

    trip_data = build_trip_plan_data(payload, route_overrides=overrides)

    assert trip_data.summary.total_driving_hours == sum(
        log.recap.driving_hours for log in trip_data.daily_logs
    )
    assert trip_data.summary.total_on_duty_hours == sum(
        log.recap.on_duty_not_driving_hours for log in trip_data.daily_logs
    )
    assert trip_data.summary.total_rest_hours == sum(
        log.recap.off_duty_hours + log.recap.sleeper_hours
        for log in trip_data.daily_logs
    )
