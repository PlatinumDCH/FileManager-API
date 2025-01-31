from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.token_model import UserTokens
from app.models.user_model import User
from app.utils.pass_serv import Hasher
from app.models.user_model import User
from app.schemes.user import ResendEmail


async def get_user_by_email(email: ResendEmail, db: AsyncSession):
    """
    Get user by him email
    :param email: email adres
    :param db: session
    :returns: User object or None
    """
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def confirmed_email(email: ResendEmail, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()
        await db.refresh(user)


async def create_new_user(body, db: AsyncSession):
    new_user = User(
        email=body.email,
        user_name=body.user_name,
        hashed_password=body.password_plain,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def exist_user(email: str, db: AsyncSession) -> bool:
    """check if email exist in tableUser, unicValue"""
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user is not None


async def get_user(email: str, db: AsyncSession):
    """return user, user email"""
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    return user


async def autenticate_user(email: str, passord: str, db: AsyncSession):
    user = await get_user(email, db)
    if not user:
        return False
    if not Hasher.verify_password(passord, user.hashed_password):
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


async def update_user_password(user: User, password: str, db: AsyncSession):
    user = await get_user_by_email(user.email, db=db)
    user.hashed_password = password
    await db.commit()
    await db.refresh(user)
    return user