from datetime import UTC, datetime

from backend.planner.domain import EventType, RouteLeg
from backend.planner.hos_engine import build_default_activities, simulate_hos_timeline


def test_pickup_and_dropoff_are_explicit_on_duty_segments():
    route_legs = [
        RouteLeg(
            name="current_to_pickup",
            origin_label="Dallas, TX",
            destination_label="Austin, TX",
            distance_miles=195,
            duration_minutes=180,
        ),
        RouteLeg(
            name="pickup_to_dropoff",
            origin_label="Austin, TX",
            destination_label="Houston, TX",
            distance_miles=165,
            duration_minutes=150,
        ),
    ]

    activities = build_default_activities(
        route_legs,
        pickup_location="Austin, TX",
        dropoff_location="Houston, TX",
    )

    assert activities[1].label == "Pickup handling"
    assert activities[1].status == EventType.ON_DUTY
    assert activities[1].duration_minutes == 60
    assert activities[3].label == "Dropoff handling"
    assert activities[3].status == EventType.ON_DUTY
    assert activities[3].duration_minutes == 60


def test_pickup_and_dropoff_count_toward_duty_window_but_not_driving():
    route_legs = [
        RouteLeg(
            name="current_to_pickup",
            origin_label="Dallas, TX",
            destination_label="Austin, TX",
            distance_miles=300,
            duration_minutes=360,
        ),
        RouteLeg(
            name="pickup_to_dropoff",
            origin_label="Austin, TX",
            destination_label="El Paso, TX",
            distance_miles=700,
            duration_minutes=420,
        ),
    ]
    activities = build_default_activities(
        route_legs,
        pickup_location="Austin, TX",
        dropoff_location="El Paso, TX",
    )

    result = simulate_hos_timeline(
        start_at=datetime(2026, 5, 25, 6, 0, tzinfo=UTC),
        current_cycle_used_hours=0,
        activities=activities,
    )

    pickup_segments = [
        segment for segment in result.timeline if segment.label == "Pickup handling"
    ]
    dropoff_segments = [
        segment for segment in result.timeline if segment.label == "Dropoff handling"
    ]
    driving_segments = [
        segment for segment in result.timeline if segment.status == EventType.DRIVING
    ]
    on_duty_segments = [
        segment for segment in result.timeline if segment.status == EventType.ON_DUTY
    ]

    assert len(pickup_segments) == 1
    assert len(dropoff_segments) == 1
    assert pickup_segments[0].duration_minutes == 60
    assert dropoff_segments[0].duration_minutes == 60
    assert sum(segment.duration_minutes for segment in on_duty_segments) == 120
    assert sum(segment.duration_minutes for segment in driving_segments) == 780
    assert any(segment.label == "10-hour off-duty reset" for segment in result.timeline)
