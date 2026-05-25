from django.urls import path

from .views import health_check, trip_plan

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("trips/plan/", trip_plan, name="trip-plan"),
]
