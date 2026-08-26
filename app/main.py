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
            "DSS Core model R2 padi-bebek (dokumen kanonik: package docs/R2, "
            "mulai dari docs/01_R2_MODEL_SSOT.md dan docs/03_R2_API_CONTRACT.md). "
            "Enam input wajib + harga beli bebek opsional (tujuh konsep "
            "pengguna). Output ilmiah/ekonomi bersifat parsial: komponen yang "
            "belum tersedia muncul sebagai null dengan status/kode alasan "
            "eksplisit pada HTTP 200. Visualisasi R2 menampilkan zona dukungan, "
            "rentang terhitung, dan waterfall finansial parsial tanpa mengarang data."
        ),
    },
    {
        "name": "optimizer",
        "description": (
            "Optimizer/rekomendasi (FITUR TERPISAH, di luar cakupan model R2). "
            "Stub berdiri sendiri; tidak reuse engine DSS core R2."
        ),
    },
]


def create_app() -> FastAPI:
    initialize_database()
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Backend Decision Support System padi-bebek (model R2).\n\n"
            "Endpoint `/api/v1/dss/simulate` menjalankan model R2 sesuai "
            "package docs/R2 (docs/01_R2_MODEL_SSOT.md, "
            "docs/03_R2_API_CONTRACT.md). Enam input wajib ditambah harga "
            "beli bebek opsional. Output ilmiah/ekonomi parsial valid: nilai "
            "yang belum tersedia (yield, pakan, biaya kandang total, profit "
            "penuh) dikembalikan sebagai null dengan status/kode alasan, "
            "bukan diisi konstanta. Simulasi terautentikasi disimpan sebagai "
            "snapshot history skema v4.\n\n"
            "Endpoint `/api/v1/dss/visualize` menyediakan view visualisasi "
            "R2 yang side-effect-free dari hasil simulasi kanonik. Endpoint "
            "`/api/v1/optimizer/recommend` adalah fitur produk terpisah "
            "(stub) di luar cakupan model R2."
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
    return JSONResponse(status_code=400, content=payload.model_dump(mode="json"))


app = create_app()
