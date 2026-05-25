from pydantic import ValidationError

from .schemas import ApiErrorResponse, ErrorCode, ValidationIssue


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
