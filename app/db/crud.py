from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.db.models.token_model import UserTokens
from app.core.security.security_password import Hasher
from app.db import schemas as shs
from app.db.models.user_model import User

async def exist_user(email: str, session: AsyncSession) -> bool:
    """check if email exist in tableUser, unicValue"""
    query = select(User).filter(User.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user is not None

async def create_new_user(body : shs.RegisterUser, session: AsyncSession):
    new_user = User(
        email=body.email,
        user_name=body.user_name,
        password=body.password,
        is_active=True,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
   
    return new_user

async def get_user_by_email(email:str, session:AsyncSession):
    result = await session.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    return user

async def autenticate_user(email: str, password: str, session: AsyncSession):
    user = await get_user_by_email(email, session)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user

async def update_token(
    user: User, token: str | None, token_type: str, db: AsyncSession
) -> None:
    """
    universal update userToken in database
    :param user: object TableUser
    :param token: new value token
    :param token_type: type token (e.g., "refresh_token")
    :parm db: session db
    :return: None
    """
    try:
        user_query = select(UserTokens).filter_by(user_id=user.id)
        result = await db.execute(user_query)
        user_tokens = result.scalar_one_or_none()

        if user_tokens:
            setattr(user_tokens, token_type, token)
            update_query = (
                update(UserTokens)
                .where(UserTokens.user_id == user.id)
                .values(**{token_type: token})
            )
            await db.execute(update_query)

        else:
            new_token = UserTokens(user_id=user.id, **{token_type: token})
            db.add(new_token)
            user_tokens = new_token

        await db.commit()
        await db.refresh(user_tokens)

    except Exception as err:
        await db.rollback()
        raise err

async def delete_user_from_db(user: User, session: AsyncSession):
    """
    delete user by ID.
    """
    await session.execute(
        delete(UserTokens).where(UserTokens.user_id == user.id)
    )

    await session.delete(user)
    await session.commit()

async def get_all_users(session:AsyncSession):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users

async def get_user_by_id(user_id:int ,session:AsyncSession):
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    return user

async def set_active_user(user_id:int ,session:AsyncSession):
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if user:
        user.is_active = False
        await session.commit()
        await session.refresh(user)
        return user
    return None

async def update_user_password(user:User, hashed_password:str, session:AsyncSession):
    """
    update user password
    :param user : sqlalchemy object user from table Users
    :param hashed_password:
    :param session:
    """
    user.password = hashed_password
    await session.commit()
    await session.refresh(user)
    return user

async def confirmed_email(user:User, session:AsyncSession, value:bool):
    user.confirmed = value
    await session.commit()
    await session.refresh(user)
    return user