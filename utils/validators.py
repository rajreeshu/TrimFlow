import re

from fastapi import HTTPException
import os
import uuid
from typing import Tuple

def validate_video_file(filename: str) -> None:
    """Validate if file is a video based on extension."""
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in valid_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Accepted types: {', '.join(valid_extensions)}"
        )

def generate_unique_filename(filename: str) -> Tuple[str, str]:
    """Generate a unique filename to avoid conflicts."""
    base_name = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    file_id = str(uuid.uuid4())
    unique_filename = f"{base_name}_{file_id}{extension}"
    unique_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', unique_filename)
    return unique_filename, file_id
