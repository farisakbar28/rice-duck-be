from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.lookups import router as lookup_router
from app.api.routes.simulations import router as simulation_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(lookup_router, prefix="/lookups", tags=["lookups"])
api_router.include_router(simulation_router, prefix="/simulations", tags=["simulations"])

