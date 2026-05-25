from ..domain import DutySegment


def normalize_timeline(segments: list[DutySegment]) -> list[DutySegment]:
    ordered_segments = sorted(
        segments,
        key=lambda segment: (
            segment.start_at,
            segment.end_at,
            segment.label,
        ),
    )

    if not ordered_segments:
        return []

    normalized: list[DutySegment] = []

    for segment in ordered_segments:
        _validate_segment(segment)

        if normalized:
            previous = normalized[-1]
            if segment.start_at < previous.end_at:
                raise ValueError(
                    "Timeline normalization failed because overlapping segments were detected."
                )

        normalized.append(segment)

    return normalized


def calculate_total_timeline_minutes(segments: list[DutySegment]) -> int:
    return sum(segment.duration_minutes for segment in segments)


def _validate_segment(segment: DutySegment) -> None:
    actual_duration = int((segment.end_at - segment.start_at).total_seconds() // 60)

    if segment.end_at < segment.start_at:
        raise ValueError("Timeline normalization failed because a segment ends before it starts.")

    if actual_duration != segment.duration_minutes:
        raise ValueError(
            "Timeline normalization failed because a segment duration does not match its timestamps."
        )
