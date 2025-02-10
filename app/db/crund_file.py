from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.files_model import Files
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Sequence
import uuid

class FileOperation:

    async def create_file(
        self, session: AsyncSession, user_id: int, file_name: str, path: str, size: int
    ):
        new_file = Files(
            user_id=user_id, file_name=file_name, file_path=path, size=size
        )
        session.add(new_file)
        try:
            await session.commit()
            await session.refresh(new_file)
            return new_file
        except SQLAlchemyError:
            await session.rollback()
            return None

    async def create_uniq_name(self, user_id, file_extesion):
        hash_name = uuid.uuid4()
        return f'{user_id}/{hash_name}.{file_extesion}'
    
    async def get_uniq_name(self, user_id, orig_file_name, session:AsyncSession):
        query = await session.execute(select(Files).where(Files.user_id == user_id, Files.file_name == orig_file_name))
        file_record = query.scalars().first()
        return file_record
    





    # async def get_file_by_id(
    #     self, session: AsyncSession, file_id: int
    # ) -> Optional[Files]:
    #     result = await session.execute(select(Files).where(Files.id == file_id))
    #     return result.scalars().first()

    # # Получить все файлы пользователя
    # async def get_files_by_user(
    #     self, session: AsyncSession, user_id: int
    # ) -> Sequence[Files]:
    #     result = await session.execute(select(Files).where(Files.user_id == user_id))
    #     return result.scalars().all()

    # async def delete_file(self, session: AsyncSession, file_id: int) -> bool:
    #     file = await self.get_file_by_id(session, file_id)
    #     if file:
    #         await session.delete(file)
    #         try:
    #             await session.commit()
    #             return True
    #         except SQLAlchemyError:
    #             await session.rollback()
    #     return False


file_manager = FileOperation()
