from telegram import Update
from telegram.ext import CallbackContext
import logging


class TelegramMessenger:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context

    async def send_text_message(self, message: str):
        if not self.update or not self.context:
            return
        try:
            # self.update.message.reply_text(message)
            await self.update.callback_query.message.reply_text(
                    text=message
                )
        except Exception as e:
            chat_id = self.update.effective_chat.id
            await self.context.bot.send_message(chat_id=chat_id, text=message)

    @staticmethod
    async def send_static_message(chat_id, text):
        """
        Send a text message from a worker process or other context
        where we don't have an instance of the messenger.
        
        Args:
            chat_id: The Telegram chat ID to send to
            text: The message text
            
        Returns:
            None
        """
        from telegram import Bot
        from config.config import config_properties
        
        try:
            bot = Bot(token=config_properties.TELEGRAM_BOT_TOKEN)
            await bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending static message: {str(e)}")