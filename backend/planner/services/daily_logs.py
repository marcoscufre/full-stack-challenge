from collections import defaultdict
from datetime import date, datetime, time, timedelta

from ..domain import DailyLogData, DailyRecapData, DutySegment, EventType


def build_daily_logs(
    timeline: list[DutySegment],
    *,
    remarks: list[str] | None = None,
) -> list[DailyLogData]:
    if not timeline:
        return []

    split_segments = _split_segments_at_midnight(timeline)
    grouped_segments: dict[date, list[DutySegment]] = defaultdict(list)

    for segment in split_segments:
        grouped_segments[segment.start_at.date()].append(segment)

    daily_logs: list[DailyLogData] = []

    for day_index, service_date in enumerate(sorted(grouped_segments.keys()), start=1):
        day_segments = grouped_segments[service_date]
        recap = _build_daily_recap(day_segments)
        daily_logs.append(
            DailyLogData(
                day_index=day_index,
                service_date=service_date,
                remarks=remarks or [],
                recap=recap,
                segments=day_segments,
            )
        )

    return daily_logs


def _split_segments_at_midnight(timeline: list[DutySegment]) -> list[DutySegment]:
    split_segments: list[DutySegment] = []

    for segment in timeline:
        current_start = segment.start_at
        current_end = segment.end_at

        while current_start.date() != current_end.date():
            midnight = datetime.combine(
                current_start.date() + timedelta(days=1),
                time.min,
                tzinfo=current_start.tzinfo,
            )
            duration_minutes = int((midnight - current_start).total_seconds() // 60)
            split_segments.append(
                _copy_segment(segment, start_at=current_start, end_at=midnight, duration_minutes=duration_minutes)
            )
            current_start = midnight

        final_duration = int((current_end - current_start).total_seconds() // 60)
        split_segments.append(
            _copy_segment(
                segment,
                start_at=current_start,
                end_at=current_end,
                duration_minutes=final_duration,
            )
        )

    return split_segments


def _build_daily_recap(segments: list[DutySegment]) -> DailyRecapData:
    off_duty_minutes = sum(
        segment.duration_minutes
        for segment in segments
        if segment.status == EventType.OFF_DUTY
    )
    sleeper_minutes = sum(
        segment.duration_minutes
        for segment in segments
        if segment.status == EventType.SLEEPER
    )
    driving_minutes = sum(
        segment.duration_minutes
        for segment in segments
        if segment.status == EventType.DRIVING
    )
    on_duty_minutes = sum(
        segment.duration_minutes
        for segment in segments
        if segment.status == EventType.ON_DUTY
    )

    return DailyRecapData(
        off_duty_hours=off_duty_minutes / 60,
        sleeper_hours=sleeper_minutes / 60,
        driving_hours=driving_minutes / 60,
        on_duty_not_driving_hours=on_duty_minutes / 60,
    )


def _copy_segment(
    segment: DutySegment,
    *,
    start_at: datetime,
    end_at: datetime,
    duration_minutes: int,
) -> DutySegment:
    return DutySegment(
        status=segment.status,
        label=segment.label,
        start_at=start_at,
        end_at=end_at,
        duration_minutes=duration_minutes,
        location=segment.location,
        notes=segment.notes,
    )
