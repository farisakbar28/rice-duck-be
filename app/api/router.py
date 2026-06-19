from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.dss import router as dss_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(dss_router, tags=["dss"])
