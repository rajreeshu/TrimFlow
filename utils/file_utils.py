import os
import aiofiles
from fastapi import UploadFile
from config.config import config_properties
import logging

logger = logging.getLogger(__name__)

async def save_file_in_chunks(file: UploadFile, file_path: str) -> None:
    """Save a large file in chunks asynchronously."""
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(config_properties.CHUNK_SIZE):
                await f.write(chunk)
        logger.info(f"File saved successfully: {file_path}")
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        raise