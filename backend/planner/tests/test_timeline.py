from datetime import UTC, datetime, timedelta

import pytest

from backend.planner.domain import DutySegment, EventType, MockRouteOverrides, RouteOverride
from backend.planner.schemas import TripPlanRequest
from backend.planner.services import build_trip_plan_data
from backend.planner.services.timeline import (
    calculate_total_timeline_minutes,
    normalize_timeline,
)


def test_timeline_normalization_returns_chronological_segments():
    start_at = datetime(2026, 5, 25, 10, 0, tzinfo=UTC)
    segments = [
        DutySegment(
            status=EventType.ON_DUTY,
            label="Second",
            start_at=start_at + timedelta(hours=1),
            end_at=start_at + timedelta(hours=2),
            duration_minutes=60,
            location="Austin, TX",
        ),
        DutySegment(
            status=EventType.DRIVING,
            label="First",
            start_at=start_at,
            end_at=start_at + timedelta(hours=1),
            duration_minutes=60,
            location="Dallas, TX -> Austin, TX",
        ),
    ]

    normalized = normalize_timeline(segments)

    assert [segment.label for segment in normalized] == ["First", "Second"]


def test_timeline_normalization_rejects_overlapping_segments():
    start_at = datetime(2026, 5, 25, 10, 0, tzinfo=UTC)
    segments = [
        DutySegment(
            status=EventType.DRIVING,
            label="First",
            start_at=start_at,
            end_at=start_at + timedelta(hours=2),
            duration_minutes=120,
            location="Dallas, TX -> Austin, TX",
        ),
        DutySegment(
            status=EventType.ON_DUTY,
            label="Overlap",
            start_at=start_at + timedelta(minutes=90),
            end_at=start_at + timedelta(hours=3),
            duration_minutes=90,
            location="Austin, TX",
        ),
    ]

    with pytest.raises(ValueError, match="overlapping segments"):
        normalize_timeline(segments)


def test_timeline_total_minutes_reconcile_with_summary():
    payload = TripPlanRequest(
        current_location="Dallas, TX",
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
        current_cycle_used_hours=0,
    )
    overrides = MockRouteOverrides(
        current_to_pickup=RouteOverride(distance_miles=180.0, duration_minutes=210),
        pickup_to_dropoff=RouteOverride(distance_miles=165.0, duration_minutes=195),
    )

    trip_data = build_trip_plan_data(payload, route_overrides=overrides)
    total_minutes = calculate_total_timeline_minutes(trip_data.timeline)

    assert total_minutes == int(trip_data.summary.total_duration_hours * 60)
    assert all(
        segment.start_at <= segment.end_at for segment in trip_data.timeline
    )
    assert all(
        trip_data.timeline[index].end_at <= trip_data.timeline[index + 1].start_at
        for index in range(len(trip_data.timeline) - 1)
    )
