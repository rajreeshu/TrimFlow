import asyncio
import logging
import sys
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
import uvicorn
import database.database_config as database_config
from config.config import config_properties
from routers.url_router import UrlRouter
from routers.video_router import VideoRouter
from telegram.ext import Application as TelegramBotApplication
from telegram_bot.handlers.video.handlers import TelegramBotHandlers
import threading

# Import for Redis connection check
from services.queue_service import check_redis_connection

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
        self.app.include_router(video_router.router)
        self.app.include_router(url_router.router)

    # Initialize database
    def initialize_database(self):
        @self.app.on_event("startup")
        async def startup():
            async with database_config.engine.begin() as conn:
                await conn.run_sync(database_config.Base.metadata.create_all)
            
            # Check Redis connection
            redis_connected = await check_redis_connection()
            if not redis_connected:
                logging.warning("Redis is not connected. Queue service will not be available. Processing will fall back to synchronous mode.")
            else:
                logging.info("Redis connection successful. Queue service is available.")
                
                # Start RQ Dashboard in a separate thread
                self.start_rq_dashboard()

    def start_rq_dashboard(self):
        """Start the RQ Dashboard for monitoring jobs in a separate thread"""
        try:
            import rq_dashboard
            from rq_dashboard import cli
            
            def run_dashboard():
                import sys
                sys.argv = [
                    'rq-dashboard',
                    '--redis-host', config_properties.REDIS_HOST,
                    '--redis-port', str(config_properties.REDIS_PORT),
                    '--redis-db', str(config_properties.REDIS_DB),
                    '--port', '9181',  # Use a different port than the main app
                    '--bind', '0.0.0.0'
                ]
                if config_properties.REDIS_PASSWORD:
                    sys.argv.extend(['--redis-password', config_properties.REDIS_PASSWORD])
                cli.main()
            
            # Start dashboard in a separate thread
            threading.Thread(target=run_dashboard, daemon=True).start()
            logging.info("RQ Dashboard started on port 9181")
        except Exception as e:
            logging.error(f"Error starting RQ Dashboard: {e}")

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

