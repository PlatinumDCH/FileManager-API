from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from backend.app.api.dependecies.security import AuthService

router = APIRouter(prefix='/auth')

templates = Jinja2Templates(directory="/Users/plarium/Develop/project/FileManager-API/frontend/templates")

@router.get('/login', response_class=HTMLResponse)
async def login_form(request:Request):
    message = request.query_params.get('message')
    error_message = request.query_params.get('error_message')
    return templates.TemplateResponse(
        'login.html',
        {
            'request':request, 
            "message": message,
            'error_message':error_message
        }
    )

@router.get('/register', response_class=HTMLResponse)
async def register_form(request:Request):
    return templates.TemplateResponse(
        'register.html',
        {
            'request':request, 
            'error_message':None
        }
    )

