from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext,CallbackQueryHandler
import re

from controllers.url_controller import UrlController
from models.video_models import VideoProcessInfo
from telegram_bot.handlers.video.video_handler_interface import MessageHandlerInterface
import telegram_bot.handlers.video.video_handler_interface as video_handler_interface

class UrlHandler(MessageHandlerInterface):
    def __init__(self):
        self.url_controller = UrlController(None)

    async def handle(self, update: Update, context: CallbackContext):
        """Handles messages containing links by forwarding them to a different service."""
        message_text = update.message.text

        # Regex to detect URLs
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, message_text)
        link = ""
        if urls:
            # Forward the first detected URL to the external service
            link = urls[0]
            if link is not None:
                # Ask for orientation
                reply_markup =  video_handler_interface.generate_question_keyboard("orientation")
                context.user_data['pending_link'] = link
                await update.message.reply_text(
                    "Select the Orientation of the Video:",
                    reply_markup=reply_markup
                )
                return

        # await self.url_controller.upload_from_url(VideoProcessInfo(), link)
