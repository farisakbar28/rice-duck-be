from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    runtime_instance_id: str = ""


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    issues: list[dict] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
