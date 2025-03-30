import asyncio
import logging
import sys
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
import uvicorn
import database.database_config as database_config
from config.config import config_properties
from routers.test_router import TestRouter
from routers.url_router import UrlRouter
from routers.video_router import VideoRouter
from telegram.ext import Application as TelegramBotApplication
from telegram_bot.handlers.video.handlers import TelegramBotHandlers

class MainApp:
    def __init__(self):
        # Create FastAPI app
        self.app = FastAPI(title="Video Trimming Service")
        self.configure_logging()
        self.include_routers()
        self.initialize_database()
        self.telegram_bot = TelegramBotApplication.builder().token(config_properties.TELEGRAM_BOT_TOKEN).build()

    # Configure logging
    def configure_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("app.log")
            ]
        )

    # Include routers
    def include_routers(self):
        video_router = VideoRouter()
        url_router = UrlRouter()
        test_router = TestRouter()
        self.app.include_router(video_router.router)
        self.app.include_router(url_router.router)
        self.app.include_router(test_router.router)

    # Initialize database
    def initialize_database(self):
        @self.app.on_event("startup")
        async def startup():
            async with database_config.engine.begin() as conn:
                await conn.run_sync(database_config.Base.metadata.create_all)


    async def run(self):
        config = uvicorn.Config("main:app", host=config_properties.BASE_URL, port=int(config_properties.PORT), reload=True)
        server = uvicorn.Server(config)
        await server.serve()

    async def run_telegram_bot(self):
        logging.info("Starting Telegram handlers...")
        handler = TelegramBotHandlers(self.telegram_bot)
        handler.add_all_handlers()
        await self.telegram_bot.initialize()
        await self.telegram_bot.start()
        await self.telegram_bot.updater.start_polling()
        logging.info("Telegram handlers started...")

    async def main(self):
        await asyncio.gather(
            self.run(),
            self.run_telegram_bot()
        )


# Create an instance of MainApp and expose the app attribute
service = MainApp()
app = service.app
# Serve the trimmed videos directory
app.mount("/media/trimmed_videos", StaticFiles(directory=config_properties.TRIMMED_DIR), name="trimmed_videos")
app.mount("/media/uploaded_videos", StaticFiles(directory=config_properties.UPLOAD_DIR), name="uploaded_videos")


# Run the FastAPI server
if __name__ == "__main__":
    asyncio.run(service.main())

