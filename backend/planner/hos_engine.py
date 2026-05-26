from datetime import datetime, timedelta

from .constants import HOS_RULES, OPERATIONAL_DEFAULTS
from .domain import (
    DutySegment,
    EventType,
    HosPlanResult,
    PlannedActivity,
    RouteLeg,
)
from .errors import ImpossibleTripError


def build_default_activities(
    route_legs: list[RouteLeg],
    *,
    pickup_location: str,
    dropoff_location: str,
    pickup_coords: tuple[float, float] | None = None,
    dropoff_coords: tuple[float, float] | None = None,
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
            notes="Real-world truck routing via OpenRouteService.",
        ),
        PlannedActivity(
            status=EventType.ON_DUTY,
            label="Pickup handling",
            location=pickup_location,
            duration_minutes=OPERATIONAL_DEFAULTS.pickup_duration_minutes,
            notes="Fixed pickup handling time based on challenge assumptions.",
            lat=pickup_coords[0] if pickup_coords else None,
            lon=pickup_coords[1] if pickup_coords else None,
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
            notes="Real-world truck routing via OpenRouteService.",
        ),
        PlannedActivity(
            status=EventType.ON_DUTY,
            label="Dropoff handling",
            location=dropoff_location,
            duration_minutes=OPERATIONAL_DEFAULTS.dropoff_duration_minutes,
            notes="Fixed dropoff handling time based on challenge assumptions.",
            lat=dropoff_coords[0] if dropoff_coords else None,
            lon=dropoff_coords[1] if dropoff_coords else None,
        ),
    ]


def simulate_hos_timeline(
    *,
    start_at: datetime,
    current_cycle_used_hours: float,
    activities: list[PlannedActivity],
) -> HosPlanResult:
    timeline: list[DutySegment] = []
    warnings = []

    current_at = start_at
    shift_start_at = start_at
    shift_driving_minutes = 0
    driving_since_break_minutes = 0
    cycle_used_minutes = int(round(current_cycle_used_hours * 60))

    # Allow starting even if cycle is exhausted by inserting a restart immediately
    if cycle_used_minutes >= (HOS_RULES.cycle_limit_hours * 60):
        current_at = _append_segment(
            timeline,
            status=EventType.OFF_DUTY,
            label="Initial 34-hour restart",
            start_at=current_at,
            duration_minutes=HOS_RULES.restart_reset_hours * 60,
            location=activities[0].location if activities else "Unknown",
            notes="Cycle limit reached before trip start. Mandatory restart applied.",
        )
        shift_start_at = current_at
        shift_driving_minutes = 0
        driving_since_break_minutes = 0
        cycle_used_minutes = 0

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

            # 1. Cycle Check (70h rule)
            if cycle_remaining <= 0:
                current_at = _append_segment(
                    timeline,
                    status=EventType.OFF_DUTY,
                    label="34-hour restart",
                    start_at=current_at,
                    duration_minutes=HOS_RULES.restart_reset_hours * 60,
                    location=activity.location,
                    notes="70-hour / 8-day cycle exhausted. Resetting cycle.",
                )
                shift_start_at = current_at
                shift_driving_minutes = 0
                driving_since_break_minutes = 0
                cycle_used_minutes = 0
                continue

            # 2. Shift Check (14h window / 11h driving)
            if duty_window_remaining <= 0 or shift_driving_remaining <= 0:
                current_at = _append_segment(
                    timeline,
                    status=EventType.OFF_DUTY,
                    label="10-hour off-duty reset",
                    start_at=current_at,
                    duration_minutes=HOS_RULES.mandatory_off_duty_reset_hours * 60,
                    location=activity.location,
                    notes="Daily duty window or driving limit reached. Mandatory rest applied.",
                )
                shift_start_at = current_at
                shift_driving_minutes = 0
                driving_since_break_minutes = 0
                continue

            # 3. Break Check (8h driving rule)
            if activity.status == EventType.DRIVING and break_remaining <= 0:
                current_at = _append_segment(
                    timeline,
                    status=EventType.OFF_DUTY,
                    label="30-minute break",
                    start_at=current_at,
                    duration_minutes=HOS_RULES.break_duration_minutes,
                    location=activity.location,
                    notes="Mandatory 30-minute break after 8 hours of driving.",
                )
                driving_since_break_minutes = 0
                continue

            # Determine size of the next chunk
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
                # Safety valve: if we are stuck, force a reset
                current_at = _append_segment(
                    timeline,
                    status=EventType.OFF_DUTY,
                    label="Emergency HOS Reset",
                    start_at=current_at,
                    duration_minutes=HOS_RULES.mandatory_off_duty_reset_hours * 60,
                    location=activity.location,
                    notes="Simulation encountered a blocked state. Forcing a 10-hour rest.",
                )
                shift_start_at = current_at
                shift_driving_minutes = 0
                driving_since_break_minutes = 0
                continue

            current_at = _append_segment(
                timeline,
                status=activity.status,
                label=activity.label,
                start_at=current_at,
                duration_minutes=next_chunk,
                location=activity.location,
                notes=activity.notes,
                lat=activity.lat,
                lon=activity.lon,
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
    lat: float | None = None,
    lon: float | None = None,
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
            lat=lat,
            lon=lon,
        )
    )
    return end_at
