import re

from telegram import Update
from telegram.ext import CallbackContext

import telegram_bot.handlers.video.video_handler_interface as video_handler_interface
from telegram_bot.handlers.video.video_handler_interface import MessageHandlerInterface


class UrlHandler(MessageHandlerInterface):

    async def handle(self, update: Update, context: CallbackContext):
        """Handles messages containing links by forwarding them to a different service."""
        message_text = update.message.text

        if context.user_data.get('awaiting_custom_input'):
            await video_handler_interface.handle_text_input(update, context)

        # Regex to detect URLs
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, message_text)
        link = ""
        if urls:
            # Forward the first detected URL to the external service
            link = urls[0]
            if link:
                context.user_data['video_info'] = link
                await video_handler_interface.start_video_processing_flow(update, context)