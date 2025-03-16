import logging

from fastapi import FastAPI

from config.database import engine, Base
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
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    def run(self):
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# Create an instance of MainApp and expose the app attribute
service = MainApp()
app = service.app
# Run the FastAPI server
if __name__ == "__main__":
    service.run()