from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.routes import minio_routes, user_routes, confirm_change_routes
from app.config.client_db import get_conn_db

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "app" / "templates" / "static"),
    name="static",
)

app.include_router(
    minio_routes.router,
    prefix='',
    tags=['minio'])

app.include_router(
    user_routes.router,
    prefix='/auth',
    tags=['register'])

app.include_router(
    confirm_change_routes.router,
    prefix='/email_process',
    tags=['confirm&changePass']
)

@app.get('/')
async def homepage():
    return {'message' : 'hello from home pages'}

@app.get("/check")
async def connect_verify(db: AsyncSession = Depends(get_conn_db)):     
    try:
        result = (await db.execute(text("SELECT 1"))).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, 
                detail="Database is not configured correctly"
            )
        return {"message": "Database is working correctly"}
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="Error connecting to the database"
        )