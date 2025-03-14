from models.database_models import OriginalVideo
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from config.database import get_db

logger = logging.getLogger(__name__)

async def save_original_video(video_data: OriginalVideo, db: AsyncSession) -> OriginalVideo:
    """Save original video data."""
    try:
        db.add(video_data)
        await db.commit()
        await db.refresh(video_data)
        return video_data
    except Exception as e:
        logger.error(f"Error saving original video data: {str(e)}")
        await db.rollback()
        raise