from fastapi import APIRouter

from backend.app.api.endpoints.processing import account_routers
from backend.app.api.endpoints.processing import admin_routes
from backend.app.api.endpoints.processing import auth_routes
from backend.app.api.endpoints.processing import files_process

from backend.app.api.endpoints.represent import auth_routes as auth_wue
from backend.app.api.endpoints.represent import account_routers as acc_rout

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


api_router.include_router(
    auth_wue.router,
    prefix='',
    tags=['register_wue']
)

api_router.include_router(
    acc_rout.router,
    prefix='',
    tags=['account_wue']
)