from ..domain import (
    DailyLogGridData,
    DutySegment,
    EventType,
    LogGridInterval,
    LogGridTransition,
)


STATUS_ROW_INDEX = {
    EventType.OFF_DUTY: 0,
    EventType.SLEEPER: 1,
    EventType.DRIVING: 2,
    EventType.ON_DUTY: 3,
}


def build_log_grid(segments: list[DutySegment]) -> DailyLogGridData:
    intervals: list[LogGridInterval] = []
    transitions: list[LogGridTransition] = []

    previous_status: EventType | None = None
    previous_end_minute: int | None = None

    for segment in segments:
        start_minute = _minute_of_day(segment.start_at)
        end_minute = _minute_of_day(segment.end_at)
        if segment.duration_minutes > 0 and end_minute == 0:
            end_minute = 1440

        interval = LogGridInterval(
            status=segment.status,
            row_index=STATUS_ROW_INDEX[segment.status],
            start_minute=start_minute,
            end_minute=end_minute,
            start_hour=start_minute / 60,
            end_hour=end_minute / 60,
            x_start=start_minute / 1440,
            x_end=end_minute / 1440,
            duration_minutes=segment.duration_minutes,
            label=segment.label,
        )
        intervals.append(interval)

        if previous_status is not None and previous_end_minute is not None:
            transitions.append(
                LogGridTransition(
                    minute=start_minute,
                    hour=start_minute / 60,
                    from_status=previous_status,
                    to_status=segment.status,
                    x_position=start_minute / 1440,
                )
            )

        previous_status = segment.status
        previous_end_minute = end_minute

    return DailyLogGridData(
        intervals=intervals,
        transitions=transitions,
        total_minutes=sum(segment.duration_minutes for segment in segments),
    )


def _minute_of_day(value) -> int:
    return (value.hour * 60) + value.minute
