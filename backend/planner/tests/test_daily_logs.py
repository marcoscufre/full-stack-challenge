from datetime import UTC, datetime

from backend.planner.domain import DutySegment, EventType, MockRouteOverrides, RouteOverride
from backend.planner.schemas import TripPlanRequest
from backend.planner.services import build_trip_plan_data
from backend.planner.services.daily_logs import build_daily_logs


def test_daily_logs_split_cross_midnight_segments_correctly():
    timeline = [
        DutySegment(
            status=EventType.DRIVING,
            label="Overnight drive",
            start_at=datetime(2026, 5, 25, 23, 0, tzinfo=UTC),
            end_at=datetime(2026, 5, 26, 2, 0, tzinfo=UTC),
            duration_minutes=180,
            location="Austin, TX -> Dallas, TX",
        )
    ]

    daily_logs = build_daily_logs(timeline, remarks=["Test trip"])

    assert len(daily_logs) == 2
    assert daily_logs[0].service_date.isoformat() == "2026-05-25"
    assert daily_logs[1].service_date.isoformat() == "2026-05-26"
    assert daily_logs[0].segments[0].duration_minutes == 60
    assert daily_logs[1].segments[0].duration_minutes == 120
    assert daily_logs[0].recap.driving_hours == 1.0
    assert daily_logs[1].recap.driving_hours == 2.0


def test_daily_logs_create_multiple_sheets_for_multi_day_trip():
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

    assert len(trip_data.daily_logs) >= 2
    assert trip_data.summary.estimated_days == len(trip_data.daily_logs)


def test_daily_log_recaps_sum_to_trip_summary():
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

    total_driving = sum(log.recap.driving_hours for log in trip_data.daily_logs)
    total_on_duty = sum(
        log.recap.on_duty_not_driving_hours for log in trip_data.daily_logs
    )
    total_off_duty = sum(log.recap.off_duty_hours for log in trip_data.daily_logs)
    total_segment_minutes = sum(
        segment.duration_minutes
        for log in trip_data.daily_logs
        for segment in log.segments
    )

    assert total_driving == trip_data.summary.total_driving_hours
    assert total_on_duty == trip_data.summary.total_on_duty_hours
    assert total_off_duty == trip_data.summary.total_rest_hours
    assert total_segment_minutes == int(trip_data.summary.total_duration_hours * 60)
