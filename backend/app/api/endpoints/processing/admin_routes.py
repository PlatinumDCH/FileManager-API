from fastapi import APIRouter, Depends
from fastapi import HTTPException, status

from backend.app.repository.manager import CRUDManager
from backend.app.api.dependecies.client_db import get_conn_db

from backend.app.api.dependecies.security import role_required 
from backend.app.db import schemas as shs

router = APIRouter(prefix='/admin')


@router.get(
    "/get-all",
    response_model=list[shs.ResponseUser],
    dependencies=[role_required("admin")],
)
async def get_all_user_admin(session=Depends(get_conn_db)):
    """
    from admin, get all user
    headers Autorization: Bearer <token>
    """
    return await CRUDManager.users.get_all_users(session)

@router.get(
        "/{user_id}", 
        response_model=shs.ResponseUser,
        dependencies=[role_required('admin')]
        )
async def get_info_user(user_id: int, session = Depends(get_conn_db)):
    """
    from admin, get all user
    headers Autorization: Bearer <token>
    """
    result = await CRUDManager.users.get_user_by_id(user_id, session)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='user not found'
        ) 
    return result

@router.put("/{user_id}/toggle-active", response_model=shs.ResponseUser)
async def block_user(user_id: int, session = Depends(get_conn_db)):
    """
    from admin, set active status user / bann
    headers Autorization: Bearer <token>
    """
    result  = await CRUDManager.users.set_active_user(user_id,session)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='user not found'
        )
    return result