from fastapi import HTTPException
from app.core.config import settings
import aiofiles
import json
from abc import ABC, abstractmethod
from pathlib import Path

class IFileExtensionChecker(ABC):

    allowed_extensions: dict
    
    @abstractmethod
    def check(self, file_name):
        pass 

class IFileExtensionLoder(ABC):

    @abstractmethod
    async def load_allowed_extensions(self):
        pass

class FileType(ABC):
    @abstractmethod
    def check_extension(self, file_extensions:str):
        pass

class ImageFileType(FileType):
    def check_extension(self, file_extensions:str):
        return 'images'

class TextFileType(FileType):
    def check_extension(self, file_extensions:str):
        return 'text'

class UnsupportedFileType(FileType):
    def check_extension(self, file_extension: str):
        return 'unsupported'
    
class FileExtensionLoader(IFileExtensionLoder):
    def __init__(self, file_path:Path):
        self.file_path = file_path
    
    async def load_allowed_extensions(self):
        try:
            async with aiofiles.open(self.file_path, mode='r') as file:
                contenst = await file.read()
                self.allowed_extensions = json.loads(contenst)
            return self.allowed_extensions
        except FileNotFoundError:
            raise HTTPException(
                status_code=500,
                detail='Allowes extensions file not found'
            )
        
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail='Error reading the allowed extensions file'
            )

class FileExtensionChecker(IFileExtensionChecker):

    def __init__(self, allowed_extensions:dict):
        self.allowed_extensions = allowed_extensions
        self.file_type_extensions = {
            'images': ImageFileType(),
            'text': TextFileType(),
        }
    
    def check(self, file_name:str):
        file_extensions = file_name.split('.')[-1]

        for file_type, strategy in self.file_type_extensions.items():
            if file_extensions in self.allowed_extensions[file_type]:
                return strategy.check_extension(file_extensions)
        return UnsupportedFileType().check_extension(file_extensions)


class FileExtensionValidator:
    def __init__(
            self, 
            extension_loader: IFileExtensionLoder, 
            extension_checker: IFileExtensionChecker
    ):
        self.extension_loader = extension_loader
        self.extension_checker = extension_checker
    
    async def validate(self, file_name: str):
        allowed_extensions = await self.extension_loader.load_allowed_extensions()
        self.extension_checker.allowed_extensions = allowed_extensions
        file_type = self.extension_checker.check(file_name)
        
        if file_type == 'unsupported':
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_name}' has an unsupported extension"
            )
        return file_type
    

    
async def get_file_extension_validator():
    loader = FileExtensionLoader(file_path=settings.FileExtensionsPath)
    checker = FileExtensionChecker(allowed_extensions={})
    return FileExtensionValidator(extension_loader=loader, extension_checker=checker)
