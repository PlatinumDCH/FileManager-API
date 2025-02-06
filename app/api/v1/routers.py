from fastapi import APIRouter

from app.api.v1.endpoints import account_routers
from app.api.v1.endpoints import admin_routes
from app.api.v1.endpoints import auth_routes

api_router = APIRouter()

api_router.include_router(
    auth_routes.router,
    prefix='',
    tags=['users']
)

api_router.include_router(
    admin_routes.router,
    prefix='',
    tags=['admin']
)

api_router.include_router(
    account_routers.router,
    prefix='',
    tags=['account']
)
