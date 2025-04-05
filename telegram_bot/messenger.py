import asyncio

from telegram import Update
from telegram.ext import CallbackContext

from telegram_bot.telegram_client import TelegramManager


class TelegramMessenger:
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

    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.telegram_client = TelegramManager.get_client()

    def send_message_with_chat_id(self, chat_id: int, message: str):
        try:
            loop = asyncio.get_running_loop()
            if loop and loop.is_running():
                # If we're already in an async context, create a task
                loop.create_task(self.telegram_client.bot.send_message(chat_id=chat_id, text=message))
            else:
                # If no loop is running, create one
                asyncio.run(self.telegram_client.bot.send_message(chat_id=chat_id, text=message))
        except Exception as e:
            print(f"Error sending message to chat ID {chat_id}: {e}")