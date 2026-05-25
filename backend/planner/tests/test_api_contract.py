import os

import django
from django.test import Client


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()


def test_health_check_returns_ok():
    client = Client()

    response = client.get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "trip-planner-api"}


def test_trip_plan_returns_stable_contract():
    client = Client()

    response = client.post(
        "/api/trips/plan/",
        data="""
        {
            "current_location": "Dallas, TX",
            "pickup_location": "Austin, TX",
            "dropoff_location": "Houston, TX",
            "current_cycle_used_hours": 12,
            "trip_start_at": "2026-05-25T10:00:00Z"
        }
        """,
        content_type="application/json",
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["request"]["current_location"] == "Dallas, TX"
    assert payload["request"]["pickup_location"] == "Austin, TX"
    assert payload["request"]["dropoff_location"] == "Houston, TX"
    assert payload["request"]["current_cycle_used_hours"] == 12.0
    assert payload["summary"]["estimated_days"] == 1
    assert payload["route_stops"][0]["type"] == "origin"
    assert payload["route_stops"][1]["type"] == "pickup"
    assert payload["route_stops"][2]["type"] == "dropoff"
    assert payload["timeline"][0]["type"] == "driving"
    assert payload["timeline"][0]["label"] == "Drive to pickup"
    assert payload["timeline"][1]["type"] == "on_duty"
    assert payload["timeline"][2]["type"] == "driving"
    assert payload["daily_logs"][0]["segments"][0]["status"] == "driving"
    assert payload["daily_logs"][0]["segments"][2]["status"] == "driving"


def test_trip_plan_rejects_invalid_payload_with_normalized_errors():
    client = Client()

    response = client.post(
        "/api/trips/plan/",
        data="""
        {
            "current_location": "",
            "pickup_location": "A",
            "dropoff_location": "Houston, TX",
            "current_cycle_used_hours": 99,
            "unexpected": true
        }
        """,
        content_type="application/json",
    )
    payload = response.json()

    assert response.status_code == 400
    assert payload["code"] == "validation_error"
    assert payload["detail"] == "Invalid request payload."
    assert isinstance(payload["errors"], list)
    assert any(error["field"] == "current_location" for error in payload["errors"])
    assert any(error["field"] == "pickup_location" for error in payload["errors"])
    assert any(error["field"] == "current_cycle_used_hours" for error in payload["errors"])
    assert any(error["field"] == "unexpected" for error in payload["errors"])


def test_trip_plan_rejects_invalid_json():
    client = Client()

    response = client.post(
        "/api/trips/plan/",
        data="{not-valid-json",
        content_type="application/json",
    )
    payload = response.json()

    assert response.status_code == 400
    assert payload == {
        "code": "invalid_json",
        "detail": "Invalid JSON payload.",
        "errors": [],
    }
