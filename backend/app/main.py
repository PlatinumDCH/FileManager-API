from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from contextlib import asynccontextmanager

from backend.services.minio_serv.manager import minio_handler
from backend.app.api.routers import api_router
from backend.app.utils.logger import logger


BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR /"frontend/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # try:
    #     await minio_handler.create_bucket()
    # except Exception as e:
    #     logger.error(f'Error cheking bucket exists')
    yield

app = FastAPI(lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR /"frontend/static"),
    name="static",
)

app.include_router(router=api_router)
@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("index.html",{
        "request":request
    })