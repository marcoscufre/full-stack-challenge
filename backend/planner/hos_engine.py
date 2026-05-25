from datetime import datetime, timedelta

from .constants import HOS_RULES, OPERATIONAL_DEFAULTS
from .domain import (
    DutySegment,
    EventType,
    HosPlanResult,
    PlannedActivity,
    RouteLeg,
)


def build_default_activities(
    route_legs: list[RouteLeg],
    *,
    pickup_location: str,
    dropoff_location: str,
) -> list[PlannedActivity]:
    if len(route_legs) != 2:
        raise ValueError(
            "Expected exactly two route legs: current_to_pickup and pickup_to_dropoff."
        )

    current_to_pickup, pickup_to_dropoff = route_legs

    return [
        PlannedActivity(
            status=EventType.DRIVING,
            label="Drive to pickup",
            location=(
                f"{current_to_pickup.origin_label} -> "
                f"{current_to_pickup.destination_label}"
            ),
            duration_minutes=current_to_pickup.duration_minutes,
            distance_miles=current_to_pickup.distance_miles,
            source_leg_name=current_to_pickup.name,
            notes="Mock route leg generated without external routing APIs.",
        ),
        PlannedActivity(
            status=EventType.ON_DUTY,
            label="Pickup handling",
            location=pickup_location,
            duration_minutes=OPERATIONAL_DEFAULTS.pickup_duration_minutes,
            notes="Fixed pickup handling time based on challenge assumptions.",
        ),
        PlannedActivity(
            status=EventType.DRIVING,
            label="Drive toward destination",
            location=(
                f"{pickup_to_dropoff.origin_label} -> "
                f"{pickup_to_dropoff.destination_label}"
            ),
            duration_minutes=pickup_to_dropoff.duration_minutes,
            distance_miles=pickup_to_dropoff.distance_miles,
            source_leg_name=pickup_to_dropoff.name,
            notes="Mock route leg generated without external routing APIs.",
        ),
        PlannedActivity(
            status=EventType.ON_DUTY,
            label="Dropoff handling",
            location=dropoff_location,
            duration_minutes=OPERATIONAL_DEFAULTS.dropoff_duration_minutes,
            notes="Fixed dropoff handling time based on challenge assumptions.",
        ),
    ]


def simulate_hos_timeline(
    *,
    start_at: datetime,
    current_cycle_used_hours: float,
    activities: list[PlannedActivity],
) -> HosPlanResult:
    timeline: list[DutySegment] = []
    warnings = [
        (
            "Cycle tracking is simplified from the current_cycle_used_hours input "
            "and does not reconstruct the driver's full prior 8-day log history."
        )
    ]

    current_at = start_at
    shift_start_at = start_at
    shift_driving_minutes = 0
    driving_since_break_minutes = 0
    cycle_used_minutes = int(round(current_cycle_used_hours * 60))

    for activity in activities:
        remaining_minutes = activity.duration_minutes

        while remaining_minutes > 0:
            cycle_remaining = (HOS_RULES.cycle_limit_hours * 60) - cycle_used_minutes
            duty_window_elapsed = int(
                (current_at - shift_start_at).total_seconds() // 60
            )
            duty_window_remaining = (
                HOS_RULES.max_on_duty_window_hours * 60
            ) - duty_window_elapsed
            shift_driving_remaining = (
                HOS_RULES.max_driving_hours_per_shift * 60
            ) - shift_driving_minutes
            break_remaining = (
                HOS_RULES.break_required_before_driving_hours * 60
            ) - driving_since_break_minutes

            if cycle_remaining <= 0:
                current_at = _append_segment(
                    timeline,
                    status=EventType.OFF_DUTY,
                    label="34-hour restart",
                    start_at=current_at,
                    duration_minutes=HOS_RULES.restart_reset_hours * 60,
                    location=activity.location,
                    notes=(
                        "Inserted because the 70-hour / 8-day cycle limit "
                        "was reached."
                    ),
                )
                shift_start_at = current_at
                shift_driving_minutes = 0
                driving_since_break_minutes = 0
                cycle_used_minutes = 0
                continue

            if duty_window_remaining <= 0 or shift_driving_remaining <= 0:
                current_at = _append_segment(
                    timeline,
                    status=EventType.OFF_DUTY,
                    label="10-hour off-duty reset",
                    start_at=current_at,
                    duration_minutes=HOS_RULES.mandatory_off_duty_reset_hours * 60,
                    location=activity.location,
                    notes=(
                        "Inserted because the driver reached the end of the "
                        "duty window or driving limit."
                    ),
                )
                shift_start_at = current_at
                shift_driving_minutes = 0
                driving_since_break_minutes = 0
                continue

            if activity.status == EventType.DRIVING and break_remaining <= 0:
                current_at = _append_segment(
                    timeline,
                    status=EventType.OFF_DUTY,
                    label="30-minute break",
                    start_at=current_at,
                    duration_minutes=HOS_RULES.break_duration_minutes,
                    location=activity.location,
                    notes=(
                        "Inserted before exceeding 8 cumulative driving hours "
                        "without a qualifying break."
                    ),
                )
                driving_since_break_minutes = 0
                continue

            if activity.status == EventType.DRIVING:
                next_chunk = min(
                    remaining_minutes,
                    cycle_remaining,
                    duty_window_remaining,
                    shift_driving_remaining,
                    break_remaining,
                )
            elif activity.status == EventType.ON_DUTY:
                next_chunk = min(
                    remaining_minutes,
                    cycle_remaining,
                    duty_window_remaining,
                )
            else:
                next_chunk = remaining_minutes

            if next_chunk <= 0:
                raise RuntimeError(
                    "Unable to allocate an HOS-compliant time chunk for the planned activity."
                )

            current_at = _append_segment(
                timeline,
                status=activity.status,
                label=activity.label,
                start_at=current_at,
                duration_minutes=next_chunk,
                location=activity.location,
                notes=activity.notes,
            )

            remaining_minutes -= next_chunk

            if activity.status == EventType.DRIVING:
                shift_driving_minutes += next_chunk
                driving_since_break_minutes += next_chunk
                cycle_used_minutes += next_chunk
            elif activity.status == EventType.ON_DUTY:
                cycle_used_minutes += next_chunk

    return HosPlanResult(timeline=timeline, warnings=warnings)


def _append_segment(
    timeline: list[DutySegment],
    *,
    status: EventType,
    label: str,
    start_at: datetime,
    duration_minutes: int,
    location: str,
    notes: str | None,
) -> datetime:
    end_at = start_at + timedelta(minutes=duration_minutes)
    timeline.append(
        DutySegment(
            status=status,
            label=label,
            start_at=start_at,
            end_at=end_at,
            duration_minutes=duration_minutes,
            location=location,
            notes=notes,
        )
    )
    return end_at
