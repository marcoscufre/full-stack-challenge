from dataclasses import dataclass


@dataclass(frozen=True)
class HosRules:
    cycle_limit_hours: int = 70
    cycle_window_days: int = 8
    max_driving_hours_per_shift: int = 11
    max_on_duty_window_hours: int = 14
    break_required_before_driving_hours: int = 8
    break_duration_minutes: int = 30
    mandatory_off_duty_reset_hours: int = 10
    restart_reset_hours: int = 34


@dataclass(frozen=True)
class OperationalDefaults:
    pickup_duration_minutes: int = 60
    dropoff_duration_minutes: int = 60
    fuel_stop_interval_miles: int = 1000
    fuel_stop_duration_minutes: int = 30
    default_mock_average_speed_mph: int = 55
    default_mock_driving_duration_hours: int = 5
    default_mock_route_distance_miles: float = 275.0


HOS_RULES = HosRules()
OPERATIONAL_DEFAULTS = OperationalDefaults()

PLANNER_ASSUMPTIONS = [
    f"Property-carrying driver under {HOS_RULES.cycle_limit_hours}-hour / {HOS_RULES.cycle_window_days}-day rules.",
    "No adverse driving conditions are applied.",
    (
        "Pickup and dropoff each consume "
        f"{OPERATIONAL_DEFAULTS.pickup_duration_minutes // 60} hour on duty, not driving."
    ),
    (
        "Fuel stops are inserted at least every "
        f"{OPERATIONAL_DEFAULTS.fuel_stop_interval_miles:,} miles in the full planner implementation."
    ),
    "Trip start defaults to the current UTC timestamp when the user does not provide one.",
]
