from typing import Optional, Any
from fastapi import UploadFile, File


class FileData:
    url : Optional[str]
    file: Optional[UploadFile] = File(None)

    def __init__(self, url: Optional[str] = None, file: Optional[UploadFile] = None):
        self.url = url
        self.file = file

    @staticmethod
    def generate(data: Any) -> 'FileData':
        if data is None:
            return FileData()

        if isinstance(data, str):
            return FileData(url=data)

        if isinstance(data, UploadFile):
            return FileData(file=data)

        if isinstance(data, dict):
            return FileData(
                url=data.get('url'),
                file=data.get('file')
            )

        raise ValueError(f"Unsupported data type: {type(data)}")

