from datetime import UTC, datetime

from ..constants import PLANNER_ASSUMPTIONS
from ..domain import (
    DailyLogData,
    DailyRecapData,
    EventType,
    MockRouteOverrides,
    PlannedStop,
    RouteSummaryData,
    StopType,
    TripPlanData,
)
from ..hos_engine import build_default_activities, simulate_hos_timeline
from ..mock_routes import resolve_mock_route_legs
from ..schemas import (
    DailyLogSheet,
    DailyLogRecap,
    DailyLogSegment,
    RouteStop,
    TimelineEvent,
    TripPlanRequest,
    TripPlanResponse,
    TripSummary,
)
from .fuel_planner import insert_fuel_stops


def build_trip_plan(payload: TripPlanRequest) -> TripPlanResponse:
    trip_data = build_trip_plan_data(payload)
    return to_trip_plan_response(payload, trip_data)


def build_trip_plan_data(
    payload: TripPlanRequest,
    route_overrides: MockRouteOverrides | None = None,
) -> TripPlanData:
    start_at = payload.trip_start_at or datetime.now(UTC).replace(microsecond=0)
    route_legs = resolve_mock_route_legs(payload, overrides=route_overrides)
    base_activities = build_default_activities(
        route_legs,
        pickup_location=payload.pickup_location,
        dropoff_location=payload.dropoff_location,
    )
    fuel_plan = insert_fuel_stops(base_activities)
    hos_plan = simulate_hos_timeline(
        start_at=start_at,
        current_cycle_used_hours=payload.current_cycle_used_hours,
        activities=fuel_plan.activities,
    )
    timeline = hos_plan.timeline

    total_driving_hours = sum(
        segment.duration_minutes
        for segment in timeline
        if segment.status == EventType.DRIVING
    ) / 60
    total_on_duty_not_driving_hours = sum(
        segment.duration_minutes
        for segment in timeline
        if segment.status == EventType.ON_DUTY
    ) / 60
    total_rest_hours = sum(
        segment.duration_minutes
        for segment in timeline
        if segment.status in {EventType.OFF_DUTY, EventType.SLEEPER}
    ) / 60

    service_dates = {
        segment.start_at.date().isoformat()
        for segment in timeline
    } | {
        segment.end_at.date().isoformat()
        for segment in timeline
    }

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
        *[
            PlannedStop(
                type=StopType.FUEL,
                label=f"Fuel stop {index}",
                location=stop.location,
                sequence=index + 2,
            )
            for index, stop in enumerate(fuel_plan.fuel_stops, start=1)
        ],
        PlannedStop(
            type=StopType.DROPOFF,
            label="Dropoff location",
            location=payload.dropoff_location,
            sequence=3 + len(fuel_plan.fuel_stops),
        ),
    ]

    summary = RouteSummaryData(
        total_distance_miles=sum(leg.distance_miles for leg in route_legs),
        total_duration_hours=sum(segment.duration_minutes for segment in timeline) / 60,
        total_driving_hours=total_driving_hours,
        total_on_duty_hours=total_on_duty_not_driving_hours,
        total_rest_hours=total_rest_hours,
        estimated_days=max(1, len(service_dates)),
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
                off_duty_hours=total_rest_hours,
                sleeper_hours=0.0,
                driving_hours=total_driving_hours,
                on_duty_not_driving_hours=total_on_duty_not_driving_hours,
            ),
            segments=timeline,
        )
    ]

    warnings = [
        "This is a scaffold response. Real geocoding, routing, fuel planning, and HOS compliance are the next implementation steps.",
        "For production-grade ELD output, the frontend should provide trip_start_at explicitly.",
        *hos_plan.warnings,
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
        fuel_stops=fuel_plan.fuel_stops,
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
