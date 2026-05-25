from pydantic import ValidationError

from .schemas import ApiErrorResponse, ErrorCode, ValidationIssue


class PlannerError(Exception):
    """Base class for all business-level planner errors."""

    def __init__(self, detail: str, code: ErrorCode = ErrorCode.PLANNER_EXECUTION_ERROR):
        self.detail = detail
        self.code = code
        super().__init__(self.detail)


class InvalidCycleUsageError(PlannerError):
    def __init__(self, detail: str):
        super().__init__(detail, code=ErrorCode.INVALID_CYCLE_USAGE)


class ImpossibleTripError(PlannerError):
    def __init__(self, detail: str):
        super().__init__(detail, code=ErrorCode.IMPOSSIBLE_TRIP)


class MockRouteError(PlannerError):
    def __init__(self, detail: str):
        super().__init__(detail, code=ErrorCode.MOCK_ROUTE_ERROR)


def build_method_not_allowed_error() -> ApiErrorResponse:
    return ApiErrorResponse(
        code=ErrorCode.METHOD_NOT_ALLOWED,
        detail="Method not allowed.",
    )


def build_invalid_json_error() -> ApiErrorResponse:
    return ApiErrorResponse(
        code=ErrorCode.INVALID_JSON,
        detail="Invalid JSON payload.",
    )


def build_validation_error(exc: ValidationError) -> ApiErrorResponse:
    issues: list[ValidationIssue] = []

    for issue in exc.errors():
        location = issue.get("loc", ())
        field = ".".join(str(part) for part in location) if location else "payload"
        issues.append(
            ValidationIssue(
                field=field,
                message=issue.get("msg", "Invalid value."),
                type=issue.get("type", "validation_error"),
            )
        )

    return ApiErrorResponse(
        code=ErrorCode.VALIDATION_ERROR,
        detail="Invalid request payload.",
        errors=issues,
    )


def build_planner_error(exc: PlannerError) -> ApiErrorResponse:
    return ApiErrorResponse(
        code=exc.code,
        detail=exc.detail,
    )


def build_internal_error() -> ApiErrorResponse:
    return ApiErrorResponse(
        code=ErrorCode.PLANNER_EXECUTION_ERROR,
        detail="An unexpected error occurred during trip planning.",
    )
