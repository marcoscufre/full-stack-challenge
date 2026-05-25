from datetime import UTC, datetime, timedelta

from .constants import OPERATIONAL_DEFAULTS, PLANNER_ASSUMPTIONS
from .domain import (
    DailyLogData,
    DailyRecapData,
    DutySegment,
    EventType,
    PlannedStop,
    RouteLeg,
    RouteSummaryData,
    StopType,
    TripPlanData,
)
from .schemas import (
    DailyLogSheet,
    DailyLogRecap,
    DailyLogSegment,
    RouteStop,
    TimelineEvent,
    TripPlanRequest,
    TripPlanResponse,
    TripSummary,
)


def build_trip_plan(payload: TripPlanRequest) -> TripPlanResponse:
    trip_data = build_trip_plan_data(payload)
    return to_trip_plan_response(payload, trip_data)


def build_trip_plan_data(payload: TripPlanRequest) -> TripPlanData:
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

    route_legs = [
        RouteLeg(
            name="pickup_to_dropoff",
            origin_label=payload.pickup_location,
            destination_label=payload.dropoff_location,
            distance_miles=OPERATIONAL_DEFAULTS.default_mock_route_distance_miles,
            duration_minutes=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours * 60,
        )
    ]

    route_stops = [
        PlannedStop(
            type=StopType.ORIGIN,
            label="Current location",
            location=payload.current_location,
            sequence=1,
        ),
        PlannedStop(
            type=StopType.PICKUP,
            label="Pickup location",
            location=payload.pickup_location,
            sequence=2,
        ),
        PlannedStop(
            type=StopType.DROPOFF,
            label="Dropoff location",
            location=payload.dropoff_location,
            sequence=3,
        ),
    ]

    timeline = [
        DutySegment(
            status=EventType.ON_DUTY,
            label="Pickup handling",
            start_at=start_at,
            end_at=pickup_end,
            duration_minutes=OPERATIONAL_DEFAULTS.pickup_duration_minutes,
            location=payload.pickup_location,
            notes="Initial placeholder event while route and HOS engine are under construction.",
        ),
        DutySegment(
            status=EventType.DRIVING,
            label="Drive toward destination",
            start_at=pickup_end,
            end_at=drive_end,
            duration_minutes=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours * 60,
            location=f"{payload.pickup_location} -> {payload.dropoff_location}",
            notes="Placeholder driving block.",
        ),
        DutySegment(
            status=EventType.ON_DUTY,
            label="Dropoff handling",
            start_at=drive_end,
            end_at=dropoff_end,
            duration_minutes=OPERATIONAL_DEFAULTS.dropoff_duration_minutes,
            location=payload.dropoff_location,
            notes="Placeholder dropoff block.",
        ),
    ]

    summary = RouteSummaryData(
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
        DailyLogData(
            day_index=1,
            service_date=start_at.date(),
            remarks=[
                f"Start: {payload.current_location}",
                f"Pickup: {payload.pickup_location}",
                f"Dropoff: {payload.dropoff_location}",
            ],
            recap=DailyRecapData(
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
                DutySegment(
                    status=EventType.ON_DUTY,
                    label="Pickup handling",
                    start_at=start_at,
                    end_at=pickup_end,
                    duration_minutes=OPERATIONAL_DEFAULTS.pickup_duration_minutes,
                    location=payload.pickup_location,
                ),
                DutySegment(
                    status=EventType.DRIVING,
                    label="Drive toward destination",
                    start_at=pickup_end,
                    end_at=drive_end,
                    duration_minutes=OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours * 60,
                    location=f"{payload.pickup_location} -> {payload.dropoff_location}",
                ),
                DutySegment(
                    status=EventType.ON_DUTY,
                    label="Dropoff handling",
                    start_at=drive_end,
                    end_at=dropoff_end,
                    duration_minutes=OPERATIONAL_DEFAULTS.dropoff_duration_minutes,
                    location=payload.dropoff_location,
                ),
            ],
        )
    ]

    warnings = [
        "This is a scaffold response. Real geocoding, routing, fuel planning, and HOS compliance are the next implementation steps.",
        "For production-grade ELD output, the frontend should provide trip_start_at explicitly.",
    ]

    return TripPlanData(
        request_snapshot=payload.model_dump(mode="json"),
        assumptions=PLANNER_ASSUMPTIONS,
        route_legs=route_legs,
        route_stops=route_stops,
        timeline=timeline,
        daily_logs=daily_logs,
        summary=summary,
        warnings=warnings,
    )


def to_trip_plan_response(
    payload: TripPlanRequest,
    trip_data: TripPlanData,
) -> TripPlanResponse:
    return TripPlanResponse(
        request=payload,
        assumptions=trip_data.assumptions,
        summary=TripSummary(
            total_distance_miles=trip_data.summary.total_distance_miles,
            total_duration_hours=trip_data.summary.total_duration_hours,
            total_driving_hours=trip_data.summary.total_driving_hours,
            total_on_duty_hours=trip_data.summary.total_on_duty_hours,
            total_rest_hours=trip_data.summary.total_rest_hours,
            estimated_days=trip_data.summary.estimated_days,
        ),
        route_stops=[
            RouteStop(
                type=stop.type,
                label=stop.label,
                location=stop.location,
                sequence=stop.sequence,
            )
            for stop in trip_data.route_stops
        ],
        timeline=[
            TimelineEvent(
                type=segment.status,
                label=segment.label,
                start_at=segment.start_at,
                end_at=segment.end_at,
                duration_minutes=segment.duration_minutes,
                location=segment.location,
                notes=segment.notes,
            )
            for segment in trip_data.timeline
        ],
        daily_logs=[
            DailyLogSheet(
                day_index=log.day_index,
                date_label=log.service_date.isoformat(),
                remarks=log.remarks,
                recap=DailyLogRecap(
                    off_duty_hours=log.recap.off_duty_hours,
                    sleeper_hours=log.recap.sleeper_hours,
                    driving_hours=log.recap.driving_hours,
                    on_duty_not_driving_hours=log.recap.on_duty_not_driving_hours,
                ),
                segments=[
                    DailyLogSegment(
                        status=segment.status,
                        start_at=segment.start_at,
                        end_at=segment.end_at,
                        duration_minutes=segment.duration_minutes,
                    )
                    for segment in log.segments
                ],
            )
            for log in trip_data.daily_logs
        ],
        warnings=trip_data.warnings,
    )
