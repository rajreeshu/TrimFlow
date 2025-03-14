import logging
from fastapi import FastAPI
from routers.video_router import router as video_router
from config.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

# Create FastAPI app
app = FastAPI(title="Video Trimming Service")

# Include routers
app.include_router(video_router)

# Initialize the database
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
