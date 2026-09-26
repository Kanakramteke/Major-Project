from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.history import router as history_router
from app.api.endpoints.patients import router as patients_router
from app.api.endpoints.predictions import router as predictions_router
from app.api.endpoints.reports import router as reports_router


api_router = APIRouter()


for route in auth_router.routes:
    api_router.routes.append(route)


for route in patients_router.routes:
    api_router.routes.append(route)


for route in predictions_router.routes:
    api_router.routes.append(route)


for route in history_router.routes:
    api_router.routes.append(route)


for route in reports_router.routes:
    api_router.routes.append(route)