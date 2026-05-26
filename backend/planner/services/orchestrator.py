from dataclasses import dataclass
from datetime import UTC, datetime

from ..constants import PLANNER_ASSUMPTIONS
from ..domain import MockRouteOverrides, PlannedStop, RouteLeg, StopType, TripPlanData
from ..hos_engine import build_default_activities, simulate_hos_timeline
from ..mock_routes import resolve_mock_route_legs
from ..schemas import TripPlanRequest, TripPlanResponse
from .daily_logs import build_daily_logs
from .fuel_planner import insert_fuel_stops
from .summary import build_trip_summary
from .timeline import normalize_timeline
from .trip_planner import to_trip_plan_response


from ..providers.geocoding import geocoder
from ..providers.routing import router
from ..errors import PlannerError, ImpossibleTripError


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

        # 1. Resolve Route Legs (Mock or Real)
        if route_overrides:
            route_legs = resolve_mock_route_legs(payload, route_overrides)
            # Use dummy coordinates for stops if mocking
            cur_lat, cur_lon = 25.7617, -80.1918 # Miami
            pic_lat, pic_lon = 26.1224, -80.1373 # Ft Lauderdale
            dro_lat, dro_lon = 26.7153, -80.0534 # West Palm Beach
            cur_name, pic_name, dro_name = payload.current_location, payload.pickup_location, payload.dropoff_location
        else:
            # 1a. Geocoding
            current_geo = geocoder.geocode(payload.current_location)
            pickup_geo = geocoder.geocode(payload.pickup_location)
            dropoff_geo = geocoder.geocode(payload.dropoff_location)

            if not (current_geo and pickup_geo and dropoff_geo):
                missing = []
                if not current_geo: missing.append(f"current: {payload.current_location}")
                if not pickup_geo: missing.append(f"pickup: {payload.pickup_location}")
                if not dropoff_geo: missing.append(f"dropoff: {payload.dropoff_location}")
                raise PlannerError(f"Could not resolve location(s): {', '.join(missing)}")

            cur, pic, dro = current_geo[0], pickup_geo[0], dropoff_geo[0]
            cur_lat, cur_lon = cur.lat, cur.lon
            pic_lat, pic_lon = pic.lat, pic.lon
            dro_lat, dro_lon = dro.lat, dro.lon
            cur_name, pic_name, dro_name = cur.display_name, pic.display_name, dro.display_name

            # 1b. Routing
            try:
                leg1_ext = router.get_directions((cur_lat, cur_lon), (pic_lat, pic_lon))
                leg2_ext = router.get_directions((pic_lat, pic_lon), (dro_lat, dro_lon))
            except Exception as e:
                raise PlannerError(f"Routing failed: {str(e)}")

            route_legs = [
                RouteLeg(
                    name="current_to_pickup",
                    origin_label=cur_name,
                    destination_label=pic_name,
                    distance_miles=leg1_ext.distance_miles,
                    duration_minutes=int(leg1_ext.duration_minutes),
                    geometry_coords=leg1_ext.geometry.coordinates if leg1_ext.geometry else None,
                ),
                RouteLeg(
                    name="pickup_to_dropoff",
                    origin_label=pic_name,
                    destination_label=dro_name,
                    distance_miles=leg2_ext.distance_miles,
                    duration_minutes=int(leg2_ext.duration_minutes),
                    geometry_coords=leg2_ext.geometry.coordinates if leg2_ext.geometry else None,
                ),
            ]

        base_activities = build_default_activities(
            route_legs,
            pickup_location=pic_name,
            dropoff_location=dro_name,
            pickup_coords=(pic_lat, pic_lon),
            dropoff_coords=(dro_lat, dro_lon),
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
                location=cur_name,
                sequence=1,
                lat=cur_lat,
                lon=cur_lon,
            ),
            PlannedStop(
                type=StopType.PICKUP,
                label="Pickup location",
                location=pic_name,
                sequence=2,
                lat=pic_lat,
                lon=pic_lon,
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
                location=dro_name,
                sequence=3 + len(fuel_plan.fuel_stops),
                lat=dro_lat,
                lon=dro_lon,
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
