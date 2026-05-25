from dataclasses import dataclass
from datetime import UTC, datetime

from ..constants import PLANNER_ASSUMPTIONS
from ..domain import MockRouteOverrides, PlannedStop, StopType, TripPlanData
from ..hos_engine import build_default_activities, simulate_hos_timeline
from ..mock_routes import resolve_mock_route_legs
from ..schemas import TripPlanRequest, TripPlanResponse
from .daily_logs import build_daily_logs
from .fuel_planner import insert_fuel_stops
from .summary import build_trip_summary
from .timeline import normalize_timeline
from .trip_planner import to_trip_plan_response


@dataclass(slots=True)
class PlannerOrchestrator:
    assumptions: list[str]

    def plan_data(
        self,
        payload: TripPlanRequest,
        route_overrides: MockRouteOverrides | None = None,
    ) -> TripPlanData:
        start_at = payload.trip_start_at or datetime.now(UTC)
        start_at = start_at.replace(second=0, microsecond=0)

        route_legs = resolve_mock_route_legs(payload, overrides=route_overrides)
        base_activities = build_default_activities(
            route_legs,
            pickup_location=payload.pickup_location,
            dropoff_location=payload.dropoff_location,
        )
        fuel_plan = insert_fuel_stops(base_activities)
        hos_plan = simulate_hos_timeline(
            start_at=start_at,
            current_cycle_used_hours=payload.current_cycle_used_hours,
            activities=fuel_plan.activities,
        )
        timeline = normalize_timeline(hos_plan.timeline)

        route_stops = [
            PlannedStop(
                type=StopType.ORIGIN,
                label="Current location",
                location=payload.current_location,
                sequence=1,
            ),
            PlannedStop(
                type=StopType.PICKUP,
                label="Pickup location",
                location=payload.pickup_location,
                sequence=2,
            ),
            *[
                PlannedStop(
                    type=StopType.FUEL,
                    label=f"Fuel stop {index}",
                    location=stop.location,
                    sequence=index + 2,
                )
                for index, stop in enumerate(fuel_plan.fuel_stops, start=1)
            ],
            PlannedStop(
                type=StopType.DROPOFF,
                label="Dropoff location",
                location=payload.dropoff_location,
                sequence=3 + len(fuel_plan.fuel_stops),
            ),
        ]

        daily_logs = build_daily_logs(
            timeline,
            remarks=[
                f"Start: {payload.current_location}",
                f"Pickup: {payload.pickup_location}",
                f"Dropoff: {payload.dropoff_location}",
            ],
        )
        summary = build_trip_summary(
            route_legs=route_legs,
            timeline=timeline,
            daily_logs=daily_logs,
        )

        warnings = [
            "This is a scaffold response. Real geocoding, routing, fuel planning, and HOS compliance are the next implementation steps.",
            "For production-grade ELD output, the frontend should provide trip_start_at explicitly.",
            *hos_plan.warnings,
        ]

        return TripPlanData(
            request_snapshot=payload.model_dump(mode="json"),
            assumptions=self.assumptions,
            route_legs=route_legs,
            route_stops=route_stops,
            timeline=timeline,
            daily_logs=daily_logs,
            summary=summary,
            warnings=warnings,
            fuel_stops=fuel_plan.fuel_stops,
        )

    def plan_response(
        self,
        payload: TripPlanRequest,
        route_overrides: MockRouteOverrides | None = None,
    ) -> TripPlanResponse:
        trip_data = self.plan_data(payload, route_overrides=route_overrides)
        return to_trip_plan_response(payload, trip_data)


planner_orchestrator = PlannerOrchestrator(assumptions=PLANNER_ASSUMPTIONS)


def build_trip_plan_data(
    payload: TripPlanRequest,
    route_overrides: MockRouteOverrides | None = None,
) -> TripPlanData:
    return planner_orchestrator.plan_data(payload, route_overrides=route_overrides)


def build_trip_plan(
    payload: TripPlanRequest,
    route_overrides: MockRouteOverrides | None = None,
) -> TripPlanResponse:
    return planner_orchestrator.plan_response(payload, route_overrides=route_overrides)
