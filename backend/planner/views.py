import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError

from .schemas import TripPlanRequest
from .services import build_trip_plan


def health_check(_: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok", "service": "trip-planner-api"})


@csrf_exempt
def trip_plan(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        raw_payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    try:
        payload = TripPlanRequest.model_validate(raw_payload)
    except ValidationError as exc:
        return JsonResponse(
            {
                "detail": "Invalid request payload.",
                "errors": exc.errors(),
            },
            status=400,
        )

    response = build_trip_plan(payload)
    return JsonResponse(response.model_dump(mode="json"), status=200)
