from fastapi import APIRouter

from app.api.endpoints import account_routers
from app.api.endpoints import admin_routes
from app.api.endpoints import auth_routes
from app.api.endpoints import files_process

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

api_router.include_router(
    files_process.router,
    prefix='',
    tags=['file_scope']
)
