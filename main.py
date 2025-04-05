import asyncio
import logging
import sys

import redis
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
import uvicorn
import database.database_config as database_config
from config import constants
from config.config import config_properties as properties
from redis_queue.redis_client import RedisManager
from routers.url_router import UrlRouter
from routers.video_router import VideoRouter
from telegram.ext import Application as TelegramBotApplication

from services.redis_service import RedisService
from telegram_bot.handlers.video.handlers import TelegramBotHandlers
from telegram_bot.telegram_client import TelegramManager


# Configure logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )


class MainApp:
    def __init__(self):
        configure_logging()
        self.app = FastAPI(title="Video Trimming Service")
        self.include_routers()
        self.initialize_database()
        self.telegram_bot = TelegramManager.get_client()
        self.redis_service = RedisService()

    # Include routers
    def include_routers(self):
        video_router = VideoRouter()
        url_router = UrlRouter()
        self.app.include_router(video_router.router)
        self.app.include_router(url_router.router)

    # Initialize database
    def initialize_database(self):
        @self.app.on_event("startup")
        def startup():
            database_config.Base.metadata.create_all(bind=database_config.engine)

    async def run_fast_api(self):
        config = uvicorn.Config("main:app", host=properties.BASE_URL, port=int(properties.PORT), reload=True)
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

    async def run_redis(self):
        redis_client = RedisManager.get_client()
        try:
            while True:
                # Wait for a job from the queue with a timeout of 1 second
                job = redis_client.brpop([constants.REDIS_VIDEO_PROCESSING_COMPLETED_QUEUE_NAME], timeout=properties.QUEUE_TIMEOUT)
                if job:
                    # job is a tuple (queue_name, item)
                    job_id = job[1]
                    self.redis_service.get_processed_video_and_upload(job_id)
                else:
                    # No job available, just print a dot to show we're alive
                    print(".", end="", flush=True)
                    await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("Shutting down job consumer...")
        except Exception as e:
            logging.info(f"Error: {e}")

    async def main(self):

        await asyncio.gather(
            self.run_fast_api(),
            self.run_telegram_bot(),
            self.run_redis()
        )


# Create an instance of MainApp and expose the app attribute
service = MainApp()
app = service.app

# Set the static file directory for uploaded videos
app.mount("/media/uploaded_videos", StaticFiles(directory=properties.UPLOAD_DIR), name="uploaded_videos")


# Run the FastAPI server
if __name__ == "__main__":
    asyncio.run(service.main())
