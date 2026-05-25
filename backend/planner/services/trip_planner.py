from ..schemas import (
    DailyLogGrid,
    DailyLogGridInterval,
    DailyLogGridTransition,
    DailyLogSheet,
    DailyLogRecap,
    DailyLogSegment,
    RouteStop,
    TimelineEvent,
    TripPlanRequest,
    TripPlanResponse,
    TripSummary,
)
from ..domain import TripPlanData


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
                grid=DailyLogGrid(
                    intervals=[
                        DailyLogGridInterval(
                            status=interval.status,
                            row_index=interval.row_index,
                            start_minute=interval.start_minute,
                            end_minute=interval.end_minute,
                            start_hour=interval.start_hour,
                            end_hour=interval.end_hour,
                            x_start=interval.x_start,
                            x_end=interval.x_end,
                            duration_minutes=interval.duration_minutes,
                            label=interval.label,
                        )
                        for interval in (log.grid.intervals if log.grid else [])
                    ],
                    transitions=[
                        DailyLogGridTransition(
                            minute=transition.minute,
                            hour=transition.hour,
                            from_status=transition.from_status,
                            to_status=transition.to_status,
                            x_position=transition.x_position,
                        )
                        for transition in (log.grid.transitions if log.grid else [])
                    ],
                    total_minutes=log.grid.total_minutes if log.grid else 0,
                    grid_start_hour=log.grid.grid_start_hour if log.grid else 0,
                    grid_end_hour=log.grid.grid_end_hour if log.grid else 24,
                ),
            )
            for log in trip_data.daily_logs
        ],
        warnings=trip_data.warnings,
    )
