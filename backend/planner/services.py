from datetime import UTC, datetime, timedelta

from .constants import OPERATIONAL_DEFAULTS, PLANNER_ASSUMPTIONS
from .schemas import (
    DailyLogSheet,
    DailyLogRecap,
    DailyLogSegment,
    EventType,
    RouteStop,
    StopType,
    TimelineEvent,
    TripPlanRequest,
    TripPlanResponse,
    TripSummary,
)


def build_trip_plan(payload: TripPlanRequest) -> TripPlanResponse:
    start_at = payload.trip_start_at or datetime.now(UTC).replace(microsecond=0)
    pickup_end = start_at + timedelta(
        minutes=OPERATIONAL_DEFAULTS.pickup_duration_minutes
    )
    drive_end = pickup_end + timedelta(
        hours=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours
    )
    dropoff_end = drive_end + timedelta(
        minutes=OPERATIONAL_DEFAULTS.dropoff_duration_minutes
    )

    route_stops = [
        RouteStop(
            type=StopType.ORIGIN,
            label="Current location",
            location=payload.current_location,
            sequence=1,
        ),
        RouteStop(
            type=StopType.PICKUP,
            label="Pickup location",
            location=payload.pickup_location,
            sequence=2,
        ),
        RouteStop(
            type=StopType.DROPOFF,
            label="Dropoff location",
            location=payload.dropoff_location,
            sequence=3,
        ),
    ]

    timeline = [
        TimelineEvent(
            type=EventType.ON_DUTY,
            label="Pickup handling",
            start_at=start_at,
            end_at=pickup_end,
            duration_minutes=OPERATIONAL_DEFAULTS.pickup_duration_minutes,
            location=payload.pickup_location,
            notes="Initial placeholder event while route and HOS engine are under construction.",
        ),
        TimelineEvent(
            type=EventType.DRIVING,
            label="Drive toward destination",
            start_at=pickup_end,
            end_at=drive_end,
            duration_minutes=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours * 60,
            location=f"{payload.pickup_location} -> {payload.dropoff_location}",
            notes="Placeholder driving block.",
        ),
        TimelineEvent(
            type=EventType.ON_DUTY,
            label="Dropoff handling",
            start_at=drive_end,
            end_at=dropoff_end,
            duration_minutes=OPERATIONAL_DEFAULTS.dropoff_duration_minutes,
            location=payload.dropoff_location,
            notes="Placeholder dropoff block.",
        ),
    ]

    summary = TripSummary(
        total_distance_miles=OPERATIONAL_DEFAULTS.default_mock_route_distance_miles,
        total_duration_hours=(
            OPERATIONAL_DEFAULTS.pickup_duration_minutes
            + OPERATIONAL_DEFAULTS.dropoff_duration_minutes
        )
        / 60
        + OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours,
        total_driving_hours=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours,
        total_on_duty_hours=(
            OPERATIONAL_DEFAULTS.pickup_duration_minutes
            + OPERATIONAL_DEFAULTS.dropoff_duration_minutes
        )
        / 60,
        total_rest_hours=0.0,
        estimated_days=1,
    )

    daily_logs = [
        DailyLogSheet(
            day_index=1,
            date_label=start_at.date().isoformat(),
            remarks=[
                f"Start: {payload.current_location}",
                f"Pickup: {payload.pickup_location}",
                f"Dropoff: {payload.dropoff_location}",
            ],
            recap=DailyLogRecap(
                off_duty_hours=0.0,
                sleeper_hours=0.0,
                driving_hours=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours,
                on_duty_not_driving_hours=(
                    OPERATIONAL_DEFAULTS.pickup_duration_minutes
                    + OPERATIONAL_DEFAULTS.dropoff_duration_minutes
                )
                / 60,
            ),
            segments=[
                DailyLogSegment(
                    status=EventType.ON_DUTY,
                    start_at=start_at,
                    end_at=pickup_end,
                    duration_minutes=OPERATIONAL_DEFAULTS.pickup_duration_minutes,
                ),
                DailyLogSegment(
                    status=EventType.DRIVING,
                    start_at=pickup_end,
                    end_at=drive_end,
                    duration_minutes=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours * 60,
                ),
                DailyLogSegment(
                    status=EventType.ON_DUTY,
                    start_at=drive_end,
                    end_at=dropoff_end,
                    duration_minutes=OPERATIONAL_DEFAULTS.dropoff_duration_minutes,
                ),
            ],
        )
    ]

    warnings = [
        "This is a scaffold response. Real geocoding, routing, fuel planning, and HOS compliance are the next implementation steps.",
        "For production-grade ELD output, the frontend should provide trip_start_at explicitly.",
    ]

    return TripPlanResponse(
        request=payload,
        assumptions=PLANNER_ASSUMPTIONS,
        summary=summary,
        route_stops=route_stops,
        timeline=timeline,
        daily_logs=daily_logs,
        warnings=warnings,
    )
