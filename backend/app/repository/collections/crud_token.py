from backend.app.db.models.user_model import User
from backend.app.db.models.token_model import UserTokens
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class TokenCrud:
    async def update_token(
        self, user: User, token: str | None, token_type: str, db: AsyncSession
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

    async def get_refresh_token(self, session: AsyncSession, user_id: int):
        result = await session.execute(
            select(UserTokens.refresh_token).filter(UserTokens.user_id == user_id)
        )
        refresh_token = result.scalar()
        return refresh_token

    
