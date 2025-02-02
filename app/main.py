from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.api.v1.routers import api_router


BASE_DIR = Path(__file__).parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "services" / "templates")

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / 'services'/ 'templates' / "static"),
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