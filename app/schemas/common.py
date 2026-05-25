from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    issues: list[dict] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
