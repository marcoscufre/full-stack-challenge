from backend.planner.constants import HOS_RULES, OPERATIONAL_DEFAULTS, PLANNER_ASSUMPTIONS


def test_hos_rules_match_challenge_assumptions():
    assert HOS_RULES.cycle_limit_hours == 70
    assert HOS_RULES.cycle_window_days == 8
    assert HOS_RULES.max_driving_hours_per_shift == 11
    assert HOS_RULES.max_on_duty_window_hours == 14
    assert HOS_RULES.break_required_before_driving_hours == 8
    assert HOS_RULES.break_duration_minutes == 30
    assert HOS_RULES.mandatory_off_duty_reset_hours == 10
    assert HOS_RULES.restart_reset_hours == 34


def test_operational_defaults_match_challenge_assumptions():
    assert OPERATIONAL_DEFAULTS.pickup_duration_minutes == 60
    assert OPERATIONAL_DEFAULTS.dropoff_duration_minutes == 60
    assert OPERATIONAL_DEFAULTS.fuel_stop_interval_miles == 1000
    assert OPERATIONAL_DEFAULTS.fuel_stop_duration_minutes == 30
    assert OPERATIONAL_DEFAULTS.default_mock_average_speed_mph > 0
    assert OPERATIONAL_DEFAULTS.default_mock_driving_duration_hours > 0
    assert OPERATIONAL_DEFAULTS.default_mock_route_distance_miles > 0


def test_planner_assumptions_are_frontend_safe_strings():
    assert len(PLANNER_ASSUMPTIONS) >= 4
    assert all(isinstance(item, str) for item in PLANNER_ASSUMPTIONS)
    assert any("70-hour / 8-day" in item for item in PLANNER_ASSUMPTIONS)
    assert any("1 hour on duty" in item for item in PLANNER_ASSUMPTIONS)
    assert any("1,000 miles" in item for item in PLANNER_ASSUMPTIONS)
