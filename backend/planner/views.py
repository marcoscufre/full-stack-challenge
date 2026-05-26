import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError

from .errors import (
    PlannerError,
    build_internal_error,
    build_invalid_json_error,
    build_method_not_allowed_error,
    build_planner_error,
    build_validation_error,
)
from .schemas import TripPlanRequest
from .services import build_trip_plan


def health_check(_: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok", "service": "trip-planner-api"})


from .providers.geocoding import geocoder
from .providers.security import rate_limit_by_ip


@csrf_exempt
@rate_limit_by_ip(limit=30, window=60)
def geocode_search(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse(build_method_not_allowed_error().model_dump(mode="json"), status=405)
    
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})
    
    try:
        results = geocoder.geocode(query)
        return JsonResponse({
            "results": [
                {
                    "lat": r.lat,
                    "lon": r.lon,
                    "display_name": r.display_name
                }
                for r in results
            ]
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@rate_limit_by_ip(limit=10, window=60)
def trip_plan(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        error = build_method_not_allowed_error()
        return JsonResponse(error.model_dump(mode="json"), status=405)

    try:
        raw_payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        error = build_invalid_json_error()
        return JsonResponse(error.model_dump(mode="json"), status=400)

    try:
        payload = TripPlanRequest.model_validate(raw_payload)
    except ValidationError as exc:
        error = build_validation_error(exc)
        return JsonResponse(error.model_dump(mode="json"), status=400)

    try:
        response = build_trip_plan(payload)
    except PlannerError as exc:
        error = build_planner_error(exc)
        return JsonResponse(error.model_dump(mode="json"), status=422)
    except Exception:
        import traceback
        traceback.print_exc()
        error = build_internal_error()
        return JsonResponse(error.model_dump(mode="json"), status=500)

    return JsonResponse(response.model_dump(mode="json"), status=200)
