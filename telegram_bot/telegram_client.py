from telegram.ext import Application as TelegramBotApplication
from typing import Optional
from config.config import config_properties as properties

class TelegramManager:
    __client: Optional[TelegramBotApplication] = None

    def __init__(self) -> None:
        raise RuntimeError("Use get_client() instead")

    @classmethod
    def get_client(cls) -> TelegramBotApplication:
        if cls.__client is None:
            try:
                cls.__client = TelegramBotApplication.builder().token(properties.TELEGRAM_BOT_TOKEN).build()
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Telegram client: {str(e)}")
        return cls.__client

    @classmethod
    async def close(cls) -> None:
        if cls.__client is not None:
            await cls.__client.shutdown()
            cls.__client = None