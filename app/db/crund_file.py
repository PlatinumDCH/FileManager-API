from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.files_model import Files
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import uuid
from typing import Sequence

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
        """generate unical name"""
        hash_name = uuid.uuid4()
        return f'{user_id}/{hash_name}.{file_extesion}'
    
    async def get_uniq_name(self, user_id, orig_file_name, session:AsyncSession):
        """get uniq name """
        query = await session.execute(select(Files).where(Files.user_id == user_id, Files.file_name == orig_file_name))
        file_record = query.scalars().first()
        return file_record
    
    async def delete_file(
            self,
            object_table:Files, 
            session:AsyncSession):
        await session.delete(object_table)
        await session.commit()

    async def get_files_by_user(
        self, session: AsyncSession, user_id: int
    ) -> Sequence[Files]:
        result = await session.execute(select(Files).where(Files.user_id == user_id))
        return result.scalars().all()

    async def update_file_record(
            self,
            session:AsyncSession,
            file_obj:Files,
            new_path:str,
            new_size:int
    ):
        """update file data"""
        file_obj.file_path = new_path
        file_obj.size = new_size
        try:
            await session.commit()
            await session.refresh(file_obj)
            return file_obj
        except SQLAlchemyError:
            await session.rollback()
            return None
        

file_manager = FileOperation()
