from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.router import api_router
from app.core.config import settings
from app.core.database import initialize_database
from app.core.exceptions import AppError
from app.schemas.common import ErrorResponse


OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Service health check untuk memastikan backend aktif.",
    },
    {
        "name": "auth",
        "description": "Auth JWT sederhana untuk menyimpan history simulasi per user.",
    },
    {
        "name": "dss",
        "description": (
            "DSS Core calculator — kalkulator SoT padi-bebek "
            "(docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md). "
            "Model A strict separation dengan output nullable dan domain guard Xiong. "
            "Tidak mengandung fitur optimizer/rekomendasi."
        ),
    },
]


def create_app() -> FastAPI:
    initialize_database()
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Backend Decision Support System padi-bebek.\n\n"
            "Endpoint `/api/v1/dss/simulate` mengikuti model SoT "
            "docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md. "
            "Tanggal/harga opsional; yield Xiong abstain di luar domain literatur. "
            "API aktif hanya mengekspos kontrak Model A yang berada dalam cakupan SoT."
        ),
        version=settings.app_version,
        debug=settings.app_debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=OPENAPI_TAGS,
        swagger_ui_parameters={"displayRequestDuration": True},
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.include_router(health_router, tags=["health"])
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    # FastAPI's JSONable encoder omits None from schema examples by default.
    # Restore explicit nulls here because unavailable Model A outputs are a
    # critical part of the public scientific contract.
    generated_openapi = app.openapi

    def model_a_openapi() -> dict:
        schema = generated_openapi()
        response_example = schema["components"]["schemas"]["DSSSimulationResponse"]["example"]
        response_example.update({
            "release_date_min": None,
            "release_date_max": None,
            "withdraw_date_min": None,
            "withdraw_date_max": None,
            "survival_risk": None,
            "yield_are_kg": None,
            "yield_total_kg": None,
            "revenue_gabah": None,
            "cost_feed_scenario": None,
            "cost_infra_cycle": None,
            "cash_contribution_before_optional": None,
            "cash_contribution_after_optional": None,
        })
        return schema

    app.openapi = model_a_openapi
    return app


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    payload = ErrorResponse(
        error={
            "code": exc.code,
            "message": exc.message,
            "field": exc.field,
            "issues": None,
        }
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    issues: list[dict] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        issues.append(
            {
                "field": location or None,
                "message": error["msg"],
                "type": error["type"],
            }
        )
    payload = ErrorResponse(
        error={
            "code": "validation_error",
            "message": "Request validation failed.",
            "field": None,
            "issues": issues,
        }
    )
    return JSONResponse(status_code=400, content=payload.model_dump(mode="json"))


app = create_app()
