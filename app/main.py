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
OPENAPI_TAGS=[{"name":"health","description":"Service health check and runtime provenance."},{"name":"auth","description":"JWT authentication for per-user A+C history."},{"name":"dss","description":"A+C dual-evidence DSS: C0 local production primary plus optional Xiong literature reference; no numeric fusion."}]
def create_app():
    initialize_database(); app=FastAPI(title=settings.app_name,description="A+C Dual-Evidence Rice-Duck DSS. Primary C0 local yield is 50 kg/are; Xiong is optional reference only and never changes economics.",version=settings.app_version,debug=settings.app_debug,docs_url="/docs",redoc_url="/redoc",openapi_tags=OPENAPI_TAGS,swagger_ui_parameters={"displayRequestDuration":True})
    app.add_middleware(CORSMiddleware,allow_origins=settings.cors_allowed_origins_list,allow_credentials=False,allow_methods=["*"],allow_headers=["*"])
    app.add_exception_handler(AppError,app_error_handler); app.add_exception_handler(RequestValidationError,validation_error_handler); app.include_router(health_router,tags=["health"]); app.include_router(api_router,prefix=settings.api_v1_prefix)
    return app
async def app_error_handler(_:Request,exc:AppError):
    return JSONResponse(status_code=exc.status_code,content=ErrorResponse(error={"code":exc.code,"message":exc.message,"field":exc.field,"issues":None}).model_dump(mode="json"))
async def validation_error_handler(_:Request,exc:RequestValidationError):
    issues=[{"field":".".join(str(part) for part in error["loc"] if part!="body") or None,"message":error["msg"],"type":error["type"]} for error in exc.errors()]
    return JSONResponse(status_code=400,content=ErrorResponse(error={"code":"validation_error","message":"Request validation failed.","field":None,"issues":issues}).model_dump(mode="json"))
app=create_app()
