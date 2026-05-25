from ..domain import DailyLogData, EventType, RouteLeg, RouteSummaryData
from .timeline import calculate_total_timeline_minutes


def build_trip_summary(
    *,
    route_legs: list[RouteLeg],
    timeline,
    daily_logs: list[DailyLogData],
) -> RouteSummaryData:
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

    return RouteSummaryData(
        total_distance_miles=sum(leg.distance_miles for leg in route_legs),
        total_duration_hours=calculate_total_timeline_minutes(timeline) / 60,
        total_driving_hours=total_driving_hours,
        total_on_duty_hours=total_on_duty_not_driving_hours,
        total_rest_hours=total_rest_hours,
        estimated_days=max(1, len(daily_logs)),
    )
