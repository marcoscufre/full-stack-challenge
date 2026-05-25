from datetime import UTC, datetime

from backend.planner.domain import DutySegment, EventType
from backend.planner.services.daily_logs import build_daily_logs
from backend.planner.services.log_grid import build_log_grid


def test_log_grid_builds_intervals_with_plotting_coordinates():
    segments = [
        DutySegment(
            status=EventType.OFF_DUTY,
            label="Off duty",
            start_at=datetime(2026, 5, 25, 0, 0, tzinfo=UTC),
            end_at=datetime(2026, 5, 25, 6, 0, tzinfo=UTC),
            duration_minutes=360,
            location="Dallas, TX",
        ),
        DutySegment(
            status=EventType.DRIVING,
            label="Drive",
            start_at=datetime(2026, 5, 25, 6, 0, tzinfo=UTC),
            end_at=datetime(2026, 5, 25, 9, 30, tzinfo=UTC),
            duration_minutes=210,
            location="Dallas, TX -> Austin, TX",
        ),
    ]

    grid = build_log_grid(segments)

    assert len(grid.intervals) == 2
    assert grid.intervals[0].row_index == 0
    assert grid.intervals[1].row_index == 2
    assert grid.intervals[1].start_minute == 360
    assert grid.intervals[1].end_minute == 570
    assert grid.intervals[1].x_start == 0.25
    assert grid.intervals[1].duration_minutes == 210


def test_log_grid_exposes_explicit_status_transitions():
    segments = [
        DutySegment(
            status=EventType.OFF_DUTY,
            label="Off duty",
            start_at=datetime(2026, 5, 25, 0, 0, tzinfo=UTC),
            end_at=datetime(2026, 5, 25, 6, 0, tzinfo=UTC),
            duration_minutes=360,
            location="Dallas, TX",
        ),
        DutySegment(
            status=EventType.DRIVING,
            label="Drive",
            start_at=datetime(2026, 5, 25, 6, 0, tzinfo=UTC),
            end_at=datetime(2026, 5, 25, 9, 30, tzinfo=UTC),
            duration_minutes=210,
            location="Dallas, TX -> Austin, TX",
        ),
        DutySegment(
            status=EventType.ON_DUTY,
            label="Fuel stop",
            start_at=datetime(2026, 5, 25, 9, 30, tzinfo=UTC),
            end_at=datetime(2026, 5, 25, 10, 0, tzinfo=UTC),
            duration_minutes=30,
            location="Waco, TX",
        ),
    ]

    grid = build_log_grid(segments)

    assert len(grid.transitions) == 2
    assert grid.transitions[0].from_status == EventType.OFF_DUTY
    assert grid.transitions[0].to_status == EventType.DRIVING
    assert grid.transitions[0].minute == 360
    assert grid.transitions[1].from_status == EventType.DRIVING
    assert grid.transitions[1].to_status == EventType.ON_DUTY
    assert grid.total_minutes == 600


def test_daily_logs_include_frontend_ready_grid_data():
    segments = [
        DutySegment(
            status=EventType.DRIVING,
            label="Overnight drive",
            start_at=datetime(2026, 5, 25, 23, 0, tzinfo=UTC),
            end_at=datetime(2026, 5, 26, 2, 0, tzinfo=UTC),
            duration_minutes=180,
            location="Austin, TX -> Dallas, TX",
        )
    ]

    daily_logs = build_daily_logs(segments, remarks=["Test trip"])

    assert len(daily_logs) == 2
    assert daily_logs[0].grid is not None
    assert daily_logs[1].grid is not None
    assert daily_logs[0].grid.intervals[0].end_minute == 1440
    assert daily_logs[1].grid.intervals[0].start_minute == 0
