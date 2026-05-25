from datetime import UTC, datetime, timedelta

from .schemas import (
    DailyLogSheet,
    RouteStop,
    TimelineEvent,
    TripPlanRequest,
    TripPlanResponse,
    TripSummary,
)


def build_trip_plan(payload: TripPlanRequest) -> TripPlanResponse:
    start_at = payload.trip_start_at or datetime.now(UTC).replace(microsecond=0)
    pickup_end = start_at + timedelta(hours=1)
    drive_end = pickup_end + timedelta(hours=5)
    dropoff_end = drive_end + timedelta(hours=1)

    assumptions = [
        "Property-carrying driver under 70-hour / 8-day rules.",
        "No adverse driving conditions are applied.",
        "Pickup and dropoff each consume 1 hour on duty, not driving.",
        "Fuel stops are inserted at least every 1,000 miles in the full planner implementation.",
        "Trip start defaults to the current UTC timestamp when the user does not provide one.",
    ]

    route_stops = [
        RouteStop(
            type="origin",
            label="Current location",
            location=payload.current_location,
            sequence=1,
        ),
        RouteStop(
            type="pickup",
            label="Pickup location",
            location=payload.pickup_location,
            sequence=2,
        ),
        RouteStop(
            type="dropoff",
            label="Dropoff location",
            location=payload.dropoff_location,
            sequence=3,
        ),
    ]

    timeline = [
        TimelineEvent(
            type="on_duty",
            label="Pickup handling",
            start_at=start_at.isoformat(),
            end_at=pickup_end.isoformat(),
            duration_minutes=60,
            location=payload.pickup_location,
            notes="Initial placeholder event while route and HOS engine are under construction.",
        ),
        TimelineEvent(
            type="driving",
            label="Drive toward destination",
            start_at=pickup_end.isoformat(),
            end_at=drive_end.isoformat(),
            duration_minutes=300,
            location=f"{payload.pickup_location} -> {payload.dropoff_location}",
            notes="Placeholder driving block.",
        ),
        TimelineEvent(
            type="on_duty",
            label="Dropoff handling",
            start_at=drive_end.isoformat(),
            end_at=dropoff_end.isoformat(),
            duration_minutes=60,
            location=payload.dropoff_location,
            notes="Placeholder dropoff block.",
        ),
    ]

    summary = TripSummary(
        total_distance_miles=275.0,
        total_duration_hours=7.0,
        total_driving_hours=5.0,
        total_on_duty_hours=2.0,
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
            recap={
                "off_duty_hours": 0.0,
                "sleeper_hours": 0.0,
                "driving_hours": 5.0,
                "on_duty_not_driving_hours": 2.0,
            },
            segments=[
                {
                    "status": "on_duty",
                    "start_at": start_at.isoformat(),
                    "end_at": pickup_end.isoformat(),
                    "duration_minutes": 60,
                },
                {
                    "status": "driving",
                    "start_at": pickup_end.isoformat(),
                    "end_at": drive_end.isoformat(),
                    "duration_minutes": 300,
                },
                {
                    "status": "on_duty",
                    "start_at": drive_end.isoformat(),
                    "end_at": dropoff_end.isoformat(),
                    "duration_minutes": 60,
                },
            ],
        )
    ]

    warnings = [
        "This is a scaffold response. Real geocoding, routing, fuel planning, and HOS compliance are the next implementation steps.",
        "For production-grade ELD output, the frontend should provide trip_start_at explicitly.",
    ]

    return TripPlanResponse(
        request=payload,
        assumptions=assumptions,
        summary=summary,
        route_stops=route_stops,
        timeline=timeline,
        daily_logs=daily_logs,
        warnings=warnings,
    )
