import json
import pytest
from django.test import Client
from .fixtures import SCENARIOS
from ..schemas import ErrorCode

@pytest.fixture
def api_client():
    return Client()

def test_health_check(api_client):
    """Verify the health check endpoint returns 200 OK."""
    response = api_client.get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "trip-planner-api"

def test_trip_plan_happy_path(api_client):
    """Verify a valid trip planning request returns 200 and a full response."""
    scenario = SCENARIOS["same_day"]()
    payload = scenario.request.model_dump(mode="json")
    
    response = api_client.post(
        "/api/trips/plan/",
        content_type="application/json",
        data=json.dumps(payload),
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Contract checks
    assert "request" in data
    assert "summary" in data
    assert "timeline" in data
    assert "daily_logs" in data
    assert "route_stops" in data
    
    # Data checks
    assert data["summary"]["total_distance_miles"] > 0
    assert len(data["timeline"]) > 0
    assert len(data["daily_logs"]) == 1

def test_trip_plan_invalid_payload(api_client):
    """Verify that an invalid payload returns 400 and a standardized error."""
    payload = {
        "current_location": "A", # Too short
        "pickup_location": "Atlanta, GA",
        "dropoff_location": "Dallas, TX",
        "current_cycle_used_hours": 10
    }
    
    response = api_client.post(
        "/api/trips/plan/",
        content_type="application/json",
        data=json.dumps(payload),
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == ErrorCode.VALIDATION_ERROR
    assert len(data["errors"]) > 0
    assert data["errors"][0]["field"] == "current_location"

def test_trip_plan_method_not_allowed(api_client):
    """Verify that GET requests to the plan endpoint are rejected."""
    response = api_client.get("/api/trips/plan/")
    assert response.status_code == 405
    data = response.json()
    assert data["code"] == ErrorCode.METHOD_NOT_ALLOWED
