from dataclasses import dataclass


@dataclass
class AppError(Exception):
    message: str
    code: str
    status_code: int
    field: str | None = None


class InvalidReferenceError(AppError):
    def __init__(self, *, message: str, field: str | None = None) -> None:
        super().__init__(
            message=message,
            code="invalid_reference",
            status_code=422,
            field=field,
        )


class ResourceNotFoundError(AppError):
    def __init__(self, *, message: str, field: str | None = None) -> None:
        super().__init__(
            message=message,
            code="not_found",
            status_code=404,
            field=field,
        )

