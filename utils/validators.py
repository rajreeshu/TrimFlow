import ast
import re

from fastapi import HTTPException
import os
import uuid
from typing import Tuple, Any


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

def parse_tuple_string(tuple_string: str) -> list[tuple[int,int]]:
    parsed_skip_pairs = None
    if tuple_string:
        try:
            # Parse string like "[[10,20],[35,40]]" to actual list of tuples
            parsed_list = ast.literal_eval(tuple_string)
            parsed_skip_pairs = [tuple(pair) for pair in parsed_list]
        except (ValueError, SyntaxError):
            raise HTTPException(status_code=400, detail="Invalid format for skip_pairs")
    if parsed_skip_pairs is None:
        parsed_skip_pairs = []
    return parsed_skip_pairs