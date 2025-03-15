from models.database_models import OriginalVideo
import logging
from config.database import SessionLocal
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def save_original_video(video_data: OriginalVideo) -> OriginalVideo:
    """Save original video data."""
    async with get_session() as db:
        try:
            db.add(video_data)
            await db.commit()
            await db.refresh(video_data)
            return video_data
        except Exception as e:
            logger.error(f"Error saving original video data: {str(e)}")
            await db.rollback()
            raise