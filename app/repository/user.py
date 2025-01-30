from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.utils.pass_serv import Hasher
from app.models.user_model import User

async def create_new_user(body, db:AsyncSession):
    new_user = User(
       email = body.email,
       hashed_password = body.password_plain,
       is_active = True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def exist_user(email:str, db: AsyncSession)->bool:
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user is not None

async def get_user(email:str,db: AsyncSession):
    """return user, user email"""
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    return user

async def autenticate_user(email:str, passord:str, db:AsyncSession):
    user = await get_user(email, db)
    if not user:
        return False
    if not Hasher.verify_password(passord, user.hashed_password):
        return False
    return user
