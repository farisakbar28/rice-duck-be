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
        "description": "Dropdown, simulasi, dan history DSS padi-bebek.",
    },
]


def create_app() -> FastAPI:
    initialize_database()
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Backend Decision Support System padi-bebek berbasis model matematika deterministik.\n\n"
            "API ini dijaga minimal untuk kebutuhan akademik: auth JWT sederhana, simulasi publik, "
            "history per user, rekomendasi grid search, dan trace perhitungan."
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
    return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))


app = create_app()
