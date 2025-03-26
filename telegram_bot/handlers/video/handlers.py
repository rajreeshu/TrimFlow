import io

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os

from controllers.url_controller import UrlController
from controllers.video_controller import VideoController
from models.video_models import VideoProcessInfo
from services.video_service import VideoService
from services.ffmpeg_service import FfmpegService
from telegram.ext import Application as TelegramBotApplication, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from fastapi import UploadFile

from telegram_bot.handlers.video.url_handler import UrlHandler
import telegram_bot.handlers.video.video_handler_interface as video_handler_interface


class TelegramBotHandlers:
    def __init__(self, telegram_bot : TelegramBotApplication):
        self.video_controller = VideoController(VideoService(FfmpegService(), None))
        self.telegram_bot  = telegram_bot
        self.url_controller = UrlController(None)

    def add_all_handlers(self):
        self.telegram_bot.add_handler(CommandHandler("start", self.start))
        self.telegram_bot.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.telegram_bot.add_handler(MessageHandler(filters.Document.VIDEO, self.handle_video))
        self.telegram_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, UrlHandler().handle))
        self.telegram_bot.add_handler(CallbackQueryHandler(video_handler_interface.handle_callback_query))

    async def start(self,update: Update, context: CallbackContext) -> None:
        """Send a welcome message with options to select."""


        # Send the message with the inline keyboard
        await update.message.reply_text(
            "Welcome"
        )

    async def handle_callback_query(self, update: Update, context: CallbackContext) -> None:
        """Handle the callback query and send a reply."""
        query = update.callback_query
        await query.answer()

        if query.data == "upload_video":
            await query.edit_message_text(text="Please upload a video.")
        elif query.data == "upload_image":
            await query.edit_message_text(text="Please upload an image.")

    async def handle_video(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(f"✅ Video is Received:")
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

            await self.video_controller.upload_video(VideoProcessInfo(),upload_file)
            await update.message.reply_text(f"✅ Video uploaded successfully:")
        except:
            await update.message.reply_text("❌ Upload failed!")

