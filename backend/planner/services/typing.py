from dataclasses import dataclass

from ..domain import FuelStopPlan, PlannedActivity


@dataclass(slots=True, frozen=True)
class FuelPlanningResult:
    activities: list[PlannedActivity]
    fuel_stops: list[FuelStopPlan]
