from datetime import UTC, datetime, timedelta

from backend.planner.domain import (
    DailyLogData,
    DailyRecapData,
    DutySegment,
    EventType,
    FuelStopPlan,
    PlannedStop,
    RestBreakPlan,
    RouteLeg,
    RouteSummaryData,
    StopType,
    TripPlanData,
)


def test_domain_models_can_represent_multi_day_trip():
    start_at = datetime(2026, 5, 25, 22, 0, tzinfo=UTC)
    overnight_end = start_at + timedelta(hours=6)
    second_day_end = overnight_end + timedelta(hours=10)

    timeline = [
        DutySegment(
            status=EventType.DRIVING,
            label="Late-night driving",
            start_at=start_at,
            end_at=overnight_end,
            duration_minutes=360,
            location="Austin, TX -> Dallas, TX",
        ),
        DutySegment(
            status=EventType.OFF_DUTY,
            label="Required rest",
            start_at=overnight_end,
            end_at=second_day_end,
            duration_minutes=600,
            location="Dallas, TX",
        ),
    ]

    trip = TripPlanData(
        request_snapshot={"current_location": "Austin, TX"},
        assumptions=["Test assumption"],
        route_legs=[
            RouteLeg(
                name="leg-1",
                origin_label="Austin, TX",
                destination_label="Dallas, TX",
                distance_miles=195,
                duration_minutes=180,
            )
        ],
        route_stops=[
            PlannedStop(
                type=StopType.ORIGIN,
                label="Current location",
                location="Austin, TX",
                sequence=1,
            ),
            PlannedStop(
                type=StopType.REST,
                label="Overnight rest",
                location="Dallas, TX",
                sequence=2,
            ),
        ],
        timeline=timeline,
        daily_logs=[
            DailyLogData(
                day_index=1,
                service_date=start_at.date(),
                remarks=["Day 1"],
                recap=DailyRecapData(
                    off_duty_hours=0,
                    sleeper_hours=0,
                    driving_hours=6,
                    on_duty_not_driving_hours=0,
                ),
                segments=[timeline[0]],
            ),
            DailyLogData(
                day_index=2,
                service_date=overnight_end.date(),
                remarks=["Day 2"],
                recap=DailyRecapData(
                    off_duty_hours=10,
                    sleeper_hours=0,
                    driving_hours=0,
                    on_duty_not_driving_hours=0,
                ),
                segments=[timeline[1]],
            ),
        ],
        summary=RouteSummaryData(
            total_distance_miles=195,
            total_duration_hours=16,
            total_driving_hours=6,
            total_on_duty_hours=0,
            total_rest_hours=10,
            estimated_days=2,
        ),
        warnings=[],
        fuel_stops=[
            FuelStopPlan(
                location="Waco, TX",
                trigger_mile_marker=120,
                duration_minutes=30,
            )
        ],
        rest_breaks=[
            RestBreakPlan(
                location="Dallas, TX",
                reason="10-hour rest",
                duration_minutes=600,
            )
        ],
    )

    assert trip.summary.estimated_days == 2
    assert trip.timeline[0].status == EventType.DRIVING
    assert trip.timeline[1].status == EventType.OFF_DUTY
    assert trip.daily_logs[1].recap.off_duty_hours == 10
    assert trip.route_stops[1].type == StopType.REST
    assert trip.fuel_stops[0].trigger_mile_marker == 120


def test_domain_models_cover_all_required_duty_states():
    statuses = {
        EventType.OFF_DUTY,
        EventType.SLEEPER,
        EventType.DRIVING,
        EventType.ON_DUTY,
    }

    assert len(statuses) == 4
