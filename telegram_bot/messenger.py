from telegram import Update
from telegram.ext import CallbackContext


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