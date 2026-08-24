from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "rice-duck-dss-backend"
    runtime_instance_id: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    issues: list[dict] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
