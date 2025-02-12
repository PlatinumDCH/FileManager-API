import pytest
from fastapi import HTTPException
from backend.app.core.config import settings
import json
from unittest.mock import AsyncMock, patch, MagicMock

from backend.app.api.dependecies.validate_file import FileExtensionLoader
from backend.app.api.dependecies.validate_file import FileExtensionChecker
from backend.app.api.dependecies.validate_file import FileExtensionValidator

@pytest.mark.asyncio
async def test_load_allowed_extensions_success():
    mock_extensions = {
        'images':['jpg','png'],
        'text_files':['txt','csv']
    }

    with patch("aiofiles.open", new_callable=MagicMock) as mock_file:
        mock_file.return_value.__aenter__.return_value.read.return_value = json.dumps(mock_extensions)

        loader = FileExtensionLoader(file_path=settings.FileExtensionsPath)
        allowed_extensions = await loader.load_allowed_extensions()

        assert allowed_extensions == mock_extensions

@pytest.mark.asyncio
async def test_load_allowed_extensions_file_not_found():
    with patch("aiofiles.open", side_effect=FileNotFoundError):
        loader = FileExtensionLoader(file_path=settings.FileExtensionsPath)
        with pytest.raises(HTTPException):
            await loader.load_allowed_extensions()


@pytest.mark.asyncio
async def test_load_allowed_extensions_json_decode_error():
    with patch("aiofiles.open", new_callable=MagicMock) as mock_file:
        mock_file.return_value.__aenter__.return_value.read.return_value = '{incorrect json}'

        loader = FileExtensionLoader(file_path=settings.FileExtensionsPath)
        with pytest.raises(HTTPException):
            await loader.load_allowed_extensions()

def test_check_valid_extensions():
    allowed_extensions = {
        'images': ['jpg', 'png'],
        'text': ['txt', 'csv']
    }

    checker = FileExtensionChecker(allowed_extensions)


    assert checker.check('image.jpg') == 'images'
    assert checker.check('image.png') == 'images'

    assert checker.check('document.txt') == 'text'
    assert checker.check('data.csv') == 'text'

    assert checker.check('file.pdf') == 'unsupported'
    
def test_check_invalid_extension():
    allowed_extensions = {
        'images': ['jpg', 'png'],
        'text': ['txt', 'csv']
    }

    checker = FileExtensionChecker(allowed_extensions)

    assert checker.check('file.exe') == 'unsupported'
    assert checker.check('file.pdf') == 'unsupported'



@pytest.mark.asyncio
async def test_validate_supported_extension():
    allowed_extensions = {
        'images': ['jpg', 'png'],
        'text': ['txt', 'csv']
    }


    loader = AsyncMock()
    loader.load_allowed_extensions.return_value = allowed_extensions

    checker = FileExtensionChecker(allowed_extensions)
    validator = FileExtensionValidator(extension_loader=loader, extension_checker=checker)

    file_type = await validator.validate('image.jpg')
    assert file_type == 'images'

    file_type = await validator.validate('document.txt')
    assert file_type == 'text'


@pytest.mark.asyncio
async def test_validate_unsupported_extension():
    allowed_extensions = {
        'images': ['jpg', 'png'],
        'text': ['txt', 'csv']
    }

    loader = AsyncMock()
    loader.load_allowed_extensions.return_value = allowed_extensions

    checker = FileExtensionChecker(allowed_extensions)
    validator = FileExtensionValidator(extension_loader=loader, extension_checker=checker)


    with pytest.raises(HTTPException) as excinfo:
        await validator.validate('file.exe')
    
    assert excinfo.value.status_code == 400
    assert "File 'file.exe' has an unsupported extension" in str(excinfo.value.detail)

