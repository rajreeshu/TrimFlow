from database.database_models import OriginalVideo, TrimmedVideo
import logging
import database.database_config as database_config
from sqlalchemy.future import select
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_session():
    """Context manager for database sessions."""
    session = database_config.SessionLocal()
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

async def get_original_video(file_id: str) -> OriginalVideo:
    async with get_session() as db:
        try:
            result = await db.execute(select(OriginalVideo).filter(OriginalVideo.video_id == file_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error retrieving original video data: {str(e)}")
            raise e

# async def get_all_original_videos() -> List[OriginalVideo]:
#     """Get all original video records."""
#     async with get_session() as db:
#         try:
#             result = await db.execute(select(OriginalVideo))
#             return result.scalars().all()
#         except Exception as e:
#             logger.error(f"Error retrieving original video data: {str(e)}")
#             raise e

async def save_trimmed_video(trimmed_video: TrimmedVideo) -> TrimmedVideo:
    async with get_session() as db:
        try:
            db.add(trimmed_video)
            await db.commit()
            await db.refresh(trimmed_video)
            return trimmed_video
        except Exception as e:
            logger.error(f"Error saving trimmed video data: {str(e)}")
            await db.rollback()
            raise