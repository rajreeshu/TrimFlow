from typing import Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application as TelegramBotApplication, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler
from telegram.ext import CallbackContext

import telegram_bot.handlers.video.video_handler_interface as video_handler_interface
from controllers.url_controller import UrlController
from telegram_bot.handlers.video.url_handler import UrlHandler
from telegram_bot.handlers.video.video_handler import VideoHandler


class TelegramBotHandlers:
    def __init__(self, telegram_bot : TelegramBotApplication):

        self.telegram_bot  = telegram_bot
        self.url_controller = UrlController(None, None)

    def add_all_handlers(self):
        self.telegram_bot.add_handler(CommandHandler("start", self.start))
        self.telegram_bot.add_handler(MessageHandler(filters.VIDEO, VideoHandler().handle))
        self.telegram_bot.add_handler(MessageHandler(filters.Document.VIDEO, VideoHandler().handle))
        self.telegram_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, UrlHandler().handle))
        self.telegram_bot.add_handler(CallbackQueryHandler(video_handler_interface.handle_callback_query))

    async def start(self,update: Update, context: CallbackContext) -> None:
        # Send the message with the inline keyboard
        await update.message.reply_text(
            "Welcome"
        )

