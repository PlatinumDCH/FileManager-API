from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import APIRouter, Form, Request, Depends
from fastapi import HTTPException, status
from fastapi.templating import Jinja2Templates
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.dependecies.client_db import get_conn_db

from backend.app.core.security.secure_token import token_manager, TokenType

from backend.app.core.security.security_password import Hasher
from backend.app.api.dependecies.security import AuthService
from backend.app.repository.manager import crud
from backend.app.db import schemas as shs
from backend.app.utils.logger import logger
from backend.services.mail_serv.email_manager import email_manager

router = APIRouter(prefix="/auth")
templates = Jinja2Templates(
    directory="/Users/plarium/Develop/project/FileManager-API/frontend/templates"
)


@router.post("/register", status_code=200)
async def register_user(
    request: Request,
    email: str = Form(...),
    user_name: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_conn_db),
):
    try:
        if await crud.users.exist_user(email, session):
            error_message = "User already exists"
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "error_message": error_message,
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        password = Hasher.get_password_hash(password)
        new_user = await crud.users.create_new_user(
            email=email, user_name=user_name, password=password, session=session
        )

        logger.info(f"Register new user {new_user.user_name}--{new_user.email}")

        # logic send email
        # await email_manager.process_email_confirmation(new_user,request,session)

        return RedirectResponse(
            url="/auth/login?message=Account successfully created. Please log in.",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        error_message = "Invalid input data"
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error_message": error_message,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/login")
async def autorization(
    request: Request,
    user_email=Form(...),
    password=Form(...),
    session: AsyncSession = Depends(get_conn_db),
):
    """
    :param form_data: fd.username, fd.password
    :session :

    autenticate user by email,password
    createAccessToken
    createRefreshToken
    save refreshToken to database
    return ResponseAutorization
    """
    user = await crud.users.autenticate_user(
        email=user_email, password=password, session=session
    )

    if not user:
        error_message = "Incorrect username or password"
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": error_message},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if user.is_active == False:
        error_message = "You are banned"
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error_message": error_message,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # todo:  validation confirmed user email adress

    encode_access_token = await token_manager.create_token(
        TokenType.ACCESS, data={"sub": user.email}, expire_delta=60
    )

    encode_refresh_token = await token_manager.create_token(
        TokenType.REFRESH, data={"sub": user.email}
    )

    await crud.tokens.update_token(user, encode_refresh_token, "refresh_token", session)

    response = JSONResponse(content={"access_token": encode_access_token})

    response.set_cookie(
        key="access_token",
        value=encode_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=encode_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    response.headers["Location"] = "/account/dashboard"
    response.status_code = status.HTTP_303_SEE_OTHER

    return response


@router.post("/logout")
async def logout(
    auth_user=Depends(AuthService().get_current_user),
    session: AsyncSession = Depends(get_conn_db),
):
    """
    clear refresh token in database
    """
    await crud.tokens.update_token(auth_user, None, TokenType.REFRESH, session)
    
    response = RedirectResponse(
        url='/',
        status_code=status.HTTP_303_SEE_OTHER
        )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response


@router.get("/me", response_model=shs.ResponseUser)
async def me(
    auth_user=Depends(AuthService().get_current_user),
):
    """
    get info about current user
    headers Autorization: Bearer <token>
    """
    return shs.ResponseUser.model_validate(auth_user)


@router.delete("/me")
async def delete_me(
    auth_user=Depends(AuthService().get_current_user),
    session: AsyncSession = Depends(get_conn_db),
):
    """
    delete user
    headers Autorization: Bearer <token>
    """
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await crud.users.delete_user_from_db(auth_user, session)
    return {"message": "User deleted succesfully"}


@router.post("/refresh-token")
async def refresh_token(request: Request, session: AsyncSession = Depends(get_conn_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing"
        )
    try:
        payload = await token_manager.decode_token(
            TokenType.REFRESH, token=refresh_token
        )
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        db_refesh = crud.tokens.get_refresh_token(session, user_email)
        if db_refesh != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
        new_access_token = await token_manager.create_token(
            TokenType.ACCESS, data={"sub": user_email}
        )
        response = JSONResponse(content={"access_token": new_access_token})
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite="lax",
        )
        return response

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token had expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    except Exception:
        pass
