from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from backend.app.api.dependecies.security import AuthService

router = APIRouter(prefix='/account')

templates = Jinja2Templates(directory="/Users/plarium/Develop/project/FileManager-API/frontend/templates")

@router.get('/dashboard', response_class=HTMLResponse)
async def dashboard(
    request:Request,
    auth_user = Depends(AuthService().get_current_user),
):
    """
    Render the dashboard page for autenticated users.
    """
    if not auth_user:
        return RedirectResponse(
            url='/auth/login',
            status_code=status.HTTP_303_SEE_OTHER
        )
    return templates.TemplateResponse(
        'dashboard.html',
        {
            'request':request,
            "user":auth_user
        }
    )
@router.get('/contacts')
async def contacts(
    request:Request,
    current_user=Depends(AuthService().get_current_user)):
    return templates.TemplateResponse(
        "contacts.html", 
        {
            'request':request,
            'user':current_user
        }
       
    )
