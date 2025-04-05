from telegram import Update
from telegram.ext import CallbackContext

from controllers.url_controller import UrlController
from controllers.video_controller import VideoController
from controllers.video_controller_interface import UploadControllerInterface
from models.file_type_model import FileData


class ControllerFactory:
    def get_upload_controller(self, file_data :FileData) -> UploadControllerInterface:
        if file_data.url is not None:
            # If the file_data contains a URL, return a UrlController
            return UrlController()
        elif file_data.file is not None:
            # If the file_data contains a file, return a VideoController
            return VideoController()

        raise ValueError("No valid file data provided")