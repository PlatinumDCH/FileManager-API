from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.templating import Jinja2Templates
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.client_minio import ensure_bucket_exists
from app.utils.logger import logger
from app.api.v1.routers import api_router
from app.api.v1.dependecies.client_db import get_conn_db
from app.core.config import settings

BASE_DIR = Path(__file__).parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "services" / 'mail' / "templates")


@asynccontextmanager
async def lifespan(app:FastAPI):
    # logger.info('Check MinIO')
    # ensure_bucket_exists(settings.BUCKET_NAME)
    yield

app = FastAPI(lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / 'services'/'mail'/'templates' /"static"),
    name="static",
)

app.include_router(router=api_router)
@app.get('/')
async def homepage():
    return {'message' : 'hello from home pages'}

# @app.get("/check")
# async def connect_verify(db: AsyncSession = Depends(get_conn_db)):     
#     try:
#         result = (await db.execute(text("SELECT 1"))).fetchone()
#         if result is None:
#             raise HTTPException(
#                 status_code=500, 
#                 detail="Database is not configured correctly"
#             )
#         return {"message": "Database is working correctly"}
#     except Exception:
#         raise HTTPException(
#             status_code=500, 
#             detail="Error connecting to the database"
#         )