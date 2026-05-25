from .typing import FuelPlanningResult

from ..constants import OPERATIONAL_DEFAULTS
from ..domain import EventType, FuelStopPlan, PlannedActivity


def insert_fuel_stops(
    activities: list[PlannedActivity],
) -> FuelPlanningResult:
    if not activities:
        return FuelPlanningResult(activities=[], fuel_stops=[])

    planned_activities: list[PlannedActivity] = []
    fuel_stops: list[FuelStopPlan] = []
    miles_since_last_fuel = 0.0
    cumulative_miles = 0.0
    interval = float(OPERATIONAL_DEFAULTS.fuel_stop_interval_miles)

    for activity in activities:
        if activity.status != EventType.DRIVING or activity.distance_miles <= 0:
            planned_activities.append(activity)
            continue

        remaining_distance = activity.distance_miles
        remaining_duration = activity.duration_minutes

        while remaining_distance > 0:
            miles_to_threshold = interval - miles_since_last_fuel

            if remaining_distance <= miles_to_threshold:
                planned_activities.append(
                    _clone_drive_activity(
                        activity,
                        duration_minutes=remaining_duration,
                        distance_miles=remaining_distance,
                    )
                )
                cumulative_miles += remaining_distance
                miles_since_last_fuel += remaining_distance
                break

            split_distance = miles_to_threshold
            split_duration = max(
                1,
                round(remaining_duration * (split_distance / remaining_distance)),
            )

            planned_activities.append(
                _clone_drive_activity(
                    activity,
                    duration_minutes=split_duration,
                    distance_miles=split_distance,
                )
            )

            cumulative_miles += split_distance
            remaining_distance -= split_distance
            remaining_duration -= split_duration
            miles_since_last_fuel = 0.0

            fuel_stop = FuelStopPlan(
                location=activity.location,
                trigger_mile_marker=cumulative_miles,
                duration_minutes=OPERATIONAL_DEFAULTS.fuel_stop_duration_minutes,
                notes="Inserted automatically after 1,000 cumulative miles.",
            )
            fuel_stops.append(fuel_stop)
            planned_activities.append(
                PlannedActivity(
                    status=EventType.ON_DUTY,
                    label="Fuel stop",
                    location=activity.location,
                    duration_minutes=OPERATIONAL_DEFAULTS.fuel_stop_duration_minutes,
                    notes=(
                        "Inserted automatically based on the challenge requirement "
                        "to fuel at least every 1,000 miles."
                    ),
                )
            )

    return FuelPlanningResult(
        activities=planned_activities,
        fuel_stops=fuel_stops,
    )


def _clone_drive_activity(
    activity: PlannedActivity,
    *,
    duration_minutes: int,
    distance_miles: float,
) -> PlannedActivity:
    return PlannedActivity(
        status=activity.status,
        label=activity.label,
        location=activity.location,
        duration_minutes=duration_minutes,
        distance_miles=distance_miles,
        source_leg_name=activity.source_leg_name,
        notes=activity.notes,
    )
