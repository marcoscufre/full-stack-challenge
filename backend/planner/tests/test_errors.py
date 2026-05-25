import json
from datetime import datetime, UTC

import pytest
from django.test import Client

from ..schemas import ErrorCode


@pytest.fixture
def api_client():
    return Client()


def test_method_not_allowed(api_client):
    response = api_client.get("/api/trips/plan/")
    assert response.status_code == 405
    data = response.json()
    assert data["code"] == ErrorCode.METHOD_NOT_ALLOWED


def test_invalid_json(api_client):
    response = api_client.post(
        "/api/trips/plan/",
        content_type="application/json",
        data="invalid json",
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == ErrorCode.INVALID_JSON


def test_validation_error(api_client):
    payload = {
        "current_location": "",  # Blank location
        "pickup_location": "B",
        "dropoff_location": "C",
        "current_cycle_used_hours": 10,
    }
    response = api_client.post(
        "/api/trips/plan/",
        content_type="application/json",
        data=json.dumps(payload),
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == ErrorCode.VALIDATION_ERROR
    assert any(e["field"] == "current_location" for e in data["errors"])


def test_impossible_trip_cycle_limit(api_client):
    payload = {
        "current_location": "Miami, FL",
        "pickup_location": "Atlanta, GA",
        "dropoff_location": "Dallas, TX",
        "current_cycle_used_hours": 70,  # Exactly at limit
        "trip_start_at": datetime.now(UTC).isoformat(),
    }
    response = api_client.post(
        "/api/trips/plan/",
        content_type="application/json",
        data=json.dumps(payload),
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == ErrorCode.IMPOSSIBLE_TRIP
    assert "cycle limit was reached" in data["detail"] or "already used 70" in data["detail"]


def test_impossible_trip_cycle_exceeded(api_client):
    # Although schema allows up to 70, let's see if HOS engine catches it if it was somehow bypassed or if we use 70.1
    # Pydantic will catch 70.1, so let's use 70.0 which is allowed by Pydantic but forbidden by HOS engine at start
    payload = {
        "current_location": "Miami, FL",
        "pickup_location": "Atlanta, GA",
        "dropoff_location": "Dallas, TX",
        "current_cycle_used_hours": 70.0,
        "trip_start_at": datetime.now(UTC).isoformat(),
    }
    response = api_client.post(
        "/api/trips/plan/",
        content_type="application/json",
        data=json.dumps(payload),
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == ErrorCode.IMPOSSIBLE_TRIP
