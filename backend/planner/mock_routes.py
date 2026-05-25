from math import ceil

from .constants import OPERATIONAL_DEFAULTS
from .domain import MockRouteOverrides, RouteLeg, RouteOverride
from .schemas import TripPlanRequest


def resolve_mock_route_legs(
    payload: TripPlanRequest,
    overrides: MockRouteOverrides | None = None,
) -> list[RouteLeg]:
    overrides = overrides or MockRouteOverrides()

    current_to_pickup = _build_leg(
        name="current_to_pickup",
        origin=payload.current_location,
        destination=payload.pickup_location,
        override=overrides.current_to_pickup,
    )
    pickup_to_dropoff = _build_leg(
        name="pickup_to_dropoff",
        origin=payload.pickup_location,
        destination=payload.dropoff_location,
        override=overrides.pickup_to_dropoff,
    )

    return [current_to_pickup, pickup_to_dropoff]


def _build_leg(
    *,
    name: str,
    origin: str,
    destination: str,
    override: RouteOverride | None,
) -> RouteLeg:
    if override is not None:
        return RouteLeg(
            name=name,
            origin_label=origin,
            destination_label=destination,
            distance_miles=override.distance_miles,
            duration_minutes=override.duration_minutes,
        )

    distance_miles = _deterministic_distance_miles(origin, destination)
    duration_minutes = _estimate_duration_minutes(distance_miles)

    return RouteLeg(
        name=name,
        origin_label=origin,
        destination_label=destination,
        distance_miles=distance_miles,
        duration_minutes=duration_minutes,
    )


def _deterministic_distance_miles(origin: str, destination: str) -> float:
    if _normalize_location(origin) == _normalize_location(destination):
        return 0.0

    pair = f"{_normalize_location(origin)}->{_normalize_location(destination)}"
    score = sum(ord(char) for char in pair)
    bucket = score % 36

    return float(75 + (bucket * 15))


def _estimate_duration_minutes(distance_miles: float) -> int:
    if distance_miles == 0:
        return 0

    raw_minutes = (
        distance_miles / OPERATIONAL_DEFAULTS.default_mock_average_speed_mph
    ) * 60
    return int(ceil(raw_minutes / 15) * 15)


def _normalize_location(value: str) -> str:
    return " ".join(value.lower().split())
