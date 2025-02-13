from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.app.db.models.token_model import UserTokens
from backend.app.core.security.security_password import Hasher
from backend.app.db.models.user_model import User


class UserCrud:

    async def exist_user(self, email: str, session: AsyncSession) -> bool:
        """check if email exist in tableUser, unicValue"""
        query = select(User).filter(User.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        return user is not None
    

    async def create_new_user(
            self, 
            email,
            user_name,
            password,
            session: AsyncSession):
        new_user = User(
            email=email,
            user_name=user_name,
            password=password,
            is_active=True,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    
        return new_user

    async def get_user_by_email(self, email:str, session:AsyncSession):
        result = await session.execute(select(User).filter(User.email == email))
        user = result.scalars().first()
        return user

    async def autenticate_user(self, email: str, password: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        if not user:
            return False
        if not Hasher.verify_password(password, user.password):
            return False
        return user

    async def delete_user_from_db(self, user: User, session: AsyncSession):
        """
        delete user by ID.
        """
        await session.execute(
            delete(UserTokens).where(UserTokens.user_id == user.id)
        )

        await session.delete(user)
        await session.commit()

    async def get_all_users(self, session:AsyncSession):
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users

    async def get_user_by_id(self, user_id:int ,session:AsyncSession):
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        return user

    async def set_active_user(self, user_id:int ,session:AsyncSession):
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if user:
            user.is_active = False
            await session.commit()
            await session.refresh(user)
            return user
        return None

    async def update_user_password(self, user:User, hashed_password:str, session:AsyncSession):
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

    async def confirmed_email(self, user:User, session:AsyncSession, value:bool):
        user.confirmed = value
        await session.commit()
        await session.refresh(user)
        return user

