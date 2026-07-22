from fastapi import APIRouter

from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.crop_explanation import router as crop_explanation_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.disease import router as disease_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.health_updates import router as health_updates_router
from app.api.v1.endpoints.location_weather import router as location_weather_router
from app.api.v1.endpoints.ndvi import router as ndvi_router
from app.api.v1.endpoints.regions import router as regions_router

api_router = APIRouter()
api_router.include_router(chat_router)
api_router.include_router(crop_explanation_router)
api_router.include_router(dashboard_router)
api_router.include_router(disease_router)
api_router.include_router(health_router)
api_router.include_router(health_updates_router)
api_router.include_router(location_weather_router)
api_router.include_router(ndvi_router)
api_router.include_router(regions_router)

