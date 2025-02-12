from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from backend.app.db.models.files_model import Files
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import uuid
from typing import Sequence


class FileOperation:

    async def create_file(
        self, session: AsyncSession, 
        user_id: int, 
        file_name: str, 
        file_path: str, 
        size: int
    ):
        """
        add NewFileObjec to database
        """
        new_file = Files(
            user_id=user_id, 
            file_name=file_name, 
            file_path=file_path, 
            size=size
        )
        session.add(new_file)
        try:
            await session.commit()
            await session.refresh(new_file)
            return new_file
        except SQLAlchemyError:
            await session.rollback()
            return None

    async def generate_uniq_filename(
            self, 
            user_id, 
            file:UploadFile,
            file_type:str):
        if not file.filename or '.' not in file.filename:
            raise ValueError("File must have a valid extension")
        file_extension = file.filename.rsplit(".")[-1]
        hash_name = uuid.uuid4()
        return f"{user_id}/{file_type}/{hash_name}.{file_extension}"

    async def get_file_record(
            self, 
            user_id, 
            orig_file_name, 
            session: AsyncSession):
        query = await session.execute(
            select(Files).where(
                Files.user_id == user_id, Files.file_name == orig_file_name
            )
        )
        file_record = query.scalars().first()
        return file_record

    async def delete_file_record(
            self, 
            object_table: Files, 
            session: AsyncSession):
        await session.delete(object_table)
        await session.commit()

    async def get_files(
        self, 
        user_id: int,
        session: AsyncSession
    ) -> Sequence[Files]:
        result = await session.execute(select(Files).where(Files.user_id == user_id))
        return result.scalars().all()

    async def update_file_record(
        self, session: AsyncSession, file_obj: Files, new_path: str, new_size: int
    ):
        """update file data"""
        file_obj.file_path = new_path
        file_obj.size = new_size
        file_obj.update_at = func.now()
        try:
            await session.commit()
            await session.refresh(file_obj)
            return file_obj
        except SQLAlchemyError:
            await session.rollback()
            return None


file_manager = FileOperation()
