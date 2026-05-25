from datetime import UTC, datetime

from backend.planner.domain import EventType, PlannedActivity, RouteLeg
from backend.planner.hos_engine import build_default_activities, simulate_hos_timeline


def test_hos_engine_inserts_break_before_exceeding_eight_hours_driving():
    start_at = datetime(2026, 5, 25, 8, 0, tzinfo=UTC)
    activities = [
        PlannedActivity(
            status=EventType.DRIVING,
            label="Long drive",
            location="Dallas, TX -> Houston, TX",
            duration_minutes=9 * 60,
        )
    ]

    result = simulate_hos_timeline(
        start_at=start_at,
        current_cycle_used_hours=0,
        activities=activities,
    )

    labels = [segment.label for segment in result.timeline]

    assert "30-minute break" in labels
    assert labels == ["Long drive", "30-minute break", "Long drive"]
    assert result.timeline[0].duration_minutes == 8 * 60
    assert result.timeline[1].duration_minutes == 30
    assert result.timeline[2].duration_minutes == 60


def test_hos_engine_stops_at_eleven_hours_and_resumes_next_day():
    start_at = datetime(2026, 5, 25, 6, 0, tzinfo=UTC)
    route_legs = [
        RouteLeg(
            name="current_to_pickup",
            origin_label="Dallas, TX",
            destination_label="Austin, TX",
            distance_miles=300,
            duration_minutes=6 * 60,
        ),
        RouteLeg(
            name="pickup_to_dropoff",
            origin_label="Austin, TX",
            destination_label="El Paso, TX",
            distance_miles=700,
            duration_minutes=7 * 60,
        ),
    ]
    activities = build_default_activities(
        route_legs,
        pickup_location="Austin, TX",
        dropoff_location="El Paso, TX",
    )

    result = simulate_hos_timeline(
        start_at=start_at,
        current_cycle_used_hours=0,
        activities=activities,
    )

    labels = [segment.label for segment in result.timeline]

    assert "10-hour off-duty reset" in labels
    assert any(segment.label == "30-minute break" for segment in result.timeline)
    assert result.timeline[-1].label == "Dropoff handling"
    assert result.timeline[-1].end_at.date().isoformat() == "2026-05-26"


def test_hos_engine_inserts_34_hour_restart_when_cycle_limit_is_reached():
    start_at = datetime(2026, 5, 25, 9, 0, tzinfo=UTC)
    activities = [
        PlannedActivity(
            status=EventType.DRIVING,
            label="Cycle-limited drive",
            location="Dallas, TX -> Austin, TX",
            duration_minutes=120,
        )
    ]

    result = simulate_hos_timeline(
        start_at=start_at,
        current_cycle_used_hours=69,
        activities=activities,
    )

    labels = [segment.label for segment in result.timeline]

    assert labels == ["Cycle-limited drive", "34-hour restart", "Cycle-limited drive"]
    assert result.timeline[0].duration_minutes == 60
    assert result.timeline[1].duration_minutes == 34 * 60
    assert result.timeline[2].duration_minutes == 60


def test_hos_engine_supports_multi_day_timeline():
    start_at = datetime(2026, 5, 25, 5, 0, tzinfo=UTC)
    activities = [
        PlannedActivity(
            status=EventType.DRIVING,
            label="Very long drive",
            location="Los Angeles, CA -> Dallas, TX",
            duration_minutes=22 * 60,
        )
    ]

    result = simulate_hos_timeline(
        start_at=start_at,
        current_cycle_used_hours=0,
        activities=activities,
    )

    assert result.timeline[0].start_at.date().isoformat() == "2026-05-25"
    assert result.timeline[-1].end_at.date().isoformat() == "2026-05-26"
    assert any(segment.label == "10-hour off-duty reset" for segment in result.timeline)
