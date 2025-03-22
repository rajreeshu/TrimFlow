import logging

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import database.database_config as database_config
from config.config import config_properties
from routers.video_router import VideoRouter


class MainApp:
    def __init__(self):
        # Create FastAPI app
        self.app = FastAPI(title="Video Trimming Service")
        self.configure_logging()
        self.include_routers()
        self.initialize_database()

    # Configure logging
    def configure_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("app.log")
            ]
        )

    # Include routers
    def include_routers(self):
        video_router = VideoRouter()
        self.app.include_router(video_router.router)

    # Initialize database
    def initialize_database(self):
        @self.app.on_event("startup")
        async def startup():
            async with database_config.engine.begin() as conn:
                await conn.run_sync(database_config.Base.metadata.create_all)


    def run(self):
        import uvicorn
        uvicorn.run("main:app", host=config_properties.BASE_URL, port=int(config_properties.PORT), reload=True)


# Create an instance of MainApp and expose the app attribute
service = MainApp()
app = service.app
# Serve the trimmed videos directory
app.mount("/media/trimmed_videos", StaticFiles(directory=config_properties.TRIMMED_DIR), name="trimmed_videos")
app.mount("/media/uploaded_videos", StaticFiles(directory=config_properties.UPLOAD_DIR), name="uploaded_videos")


# Run the FastAPI server
if __name__ == "__main__":
    service.run()