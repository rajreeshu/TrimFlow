import io
import os

from fastapi import UploadFile
from telegram import Update
from telegram.ext import CallbackContext
import telegram_bot.handlers.video.video_handler_interface as video_handler_interface
from controllers.video_controller import VideoController
from telegram_bot.handlers.video.video_handler_interface import MessageHandlerInterface


class VideoHandler(MessageHandlerInterface):

    async def handle(self, update: Update, context: CallbackContext) -> None:
        video = update.message.video
        if video is None:
            video = update.message.document
        # Check file size
        if video.file_size > 50 * 1024 * 1024:  # 50 MB
            await update.message.reply_text("❌ The file is too large! Please send a file smaller than 50 MB.")
            return

        """Handles video messages by downloading and uploading them to FastAPI."""
        try:
            file = await update.message.video.get_file()
        except:
            file = await update.message.document.get_file()

        file_path = await file.download_to_drive()

        try:
            """hello"""
            with open(file_path, "rb") as f:
                # file_content = {"file": (os.path.basename(file_path), f, "video/mp4")}
                file_content = f.read()

                # Create a SpooledTemporaryFile for the UploadFile
                spooled_file = io.BytesIO(file_content)

                # Create an UploadFile object
                upload_file = UploadFile(
                    filename=os.path.basename(file_path),
                    file=spooled_file,
                )
                context.user_data['video_info'] = upload_file
                await video_handler_interface.start_video_processing_flow(update, context)

        except:
            await update.message.reply_text("❌ Upload failed!")