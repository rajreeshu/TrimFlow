import os
import logging
import json
import platform
from redis import Redis
from rq import Queue
from rq.job import Job

from config.config import config_properties
from models.video_models import VideoInfo, ProcessingStatus, VideoProcessInfo
from services.ffmpeg_service import FfmpegService
from database.repository.original_video_repository import OriginalVideoRepository
from database.repository.trimmed_video_repository import TrimmedVideoRepository
from database.database_models import TrimmedVideo
from datetime import timedelta
import utils.validators as validators
import asyncio

logger = logging.getLogger(__name__)

# Initialize Redis connection with retries and exception handling
def get_redis_connection():
    try:
        # Redis connection parameters
        redis_params = {
            'host': config_properties.REDIS_HOST,
            'port': config_properties.REDIS_PORT,
            'db': config_properties.REDIS_DB,
            'socket_connect_timeout': 5  # Add timeout to avoid long blocking
        }
        
        # Only add password if it's set
        if config_properties.REDIS_PASSWORD:
            redis_params['password'] = config_properties.REDIS_PASSWORD
            
        # Create Redis connection
        redis_conn = Redis(**redis_params)
        return redis_conn
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {str(e)}")
        return None

# Initialize queue with None - it will be created on-demand
redis_conn = None
video_queue = None

# Asynchronous function to check if Redis is running
async def check_redis_connection():
    global redis_conn, video_queue
    
    try:
        # Initialize connection if not already done
        if redis_conn is None:
            redis_conn = get_redis_connection()
            
        # Check if we have a valid connection
        if redis_conn is None:
            return False
            
        # Try to ping Redis
        is_connected = redis_conn.ping()
        
        # If connected and queue not initialized, create it
        if is_connected and video_queue is None:
            video_queue = Queue(config_properties.REDIS_QUEUE_NAME, connection=redis_conn)
            
        return is_connected
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        return False

# Process video function to be called by worker
def process_video_job(video_info_dict, video_process_info_dict, chat_id=None):
    """
    Worker function to process a video. This runs in a separate process.
    
    Args:
        video_info_dict: Dictionary representation of VideoInfo
        video_process_info_dict: Dictionary representation of VideoProcessInfo
        chat_id: Optional Telegram chat ID for notifications
    
    Returns:
        Updated VideoInfo dictionary
    """
    try:
        logger.info(f"Starting video processing job for file ID: {video_info_dict['file_id']}")
        
        # Convert dictionaries back to objects
        video_info = VideoInfo(**video_info_dict)
        video_process_info = VideoProcessInfo(**video_process_info_dict)
        
        # Process the video
        ffmpeg_service = FfmpegService()
        updated_info = ffmpeg_service.trim_video(video_info, video_process_info)
        
        # Save to database using synchronous methods since RQ doesn't support asyncio directly
        original_video_repo = OriginalVideoRepository()
        trimmed_video_repo = TrimmedVideoRepository()
        
        # Check if there's a running event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            # No event loop exists yet
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Use a running loop or create a new one
        original_video_db_data = loop.run_until_complete(
            original_video_repo.get_by_columns({"video_id": video_info.file_id})
        )
        
        if not original_video_db_data:
            logger.error(f"No original video found in database for ID: {video_info.file_id}")
            return video_info.__dict__
            
        original_video_db_data = original_video_db_data[0]
        
        # Save each segment to the database
        for segment in updated_info.segments:
            trimmed_video = TrimmedVideo(
                original_video_id=original_video_db_data.id,
                start_time=timedelta(seconds=0),
                end_time=timedelta(seconds=0),
                remark="",
                description="",
                hashtags=[],
                thumbnail=None,
                file_name=segment,
                location=os.path.join(config_properties.TRIMMED_DIR, segment)
            )
            loop.run_until_complete(trimmed_video_repo.save(trimmed_video))
            
            # Send notification if chat_id is provided
            if chat_id:
                from telegram_bot.messenger import TelegramMessenger
                full_path = validators.generate_full_path_from_location(
                    os.path.join(config_properties.TRIMMED_DIR, segment).replace("\\", "/")
                )
                loop.run_until_complete(TelegramMessenger.send_static_message(chat_id, full_path))
        
        # No need to close the loop if it was already running
        
        logger.info(f"Video processing job completed for file ID: {video_info.file_id}")
        return updated_info.__dict__
        
    except Exception as e:
        logger.error(f"Error in video processing job: {str(e)}")
        video_info.status = ProcessingStatus.FAILED
        video_info.error = f"Processing error: {str(e)}"
        return video_info.__dict__

# Enqueue a video processing job
def enqueue_video_processing(video_info: VideoInfo, video_process_info: VideoProcessInfo, chat_id=None):
    """
    Enqueue a video processing job to Redis Queue
    
    Args:
        video_info: VideoInfo object
        video_process_info: VideoProcessInfo object
        chat_id: Optional Telegram chat ID for notifications
    
    Returns:
        Job ID or None if queue is not available
    """
    global redis_conn, video_queue
    
    try:
        # Ensure we have Redis connection and queue
        if redis_conn is None:
            redis_conn = get_redis_connection()
        
        if redis_conn is None:
            logger.error("Cannot enqueue job: Redis connection unavailable")
            video_info.status = ProcessingStatus.FAILED
            video_info.error = "Redis connection unavailable - processed synchronously"
            # Process synchronously as fallback
            ffmpeg_service = FfmpegService()
            ffmpeg_service.trim_video(video_info, video_process_info)
            return "no_queue_fallback"
        
        if video_queue is None:
            video_queue = Queue(config_properties.REDIS_QUEUE_NAME, connection=redis_conn)
            
        # Convert objects to dictionaries for serialization
        video_info_dict = video_info.__dict__
        video_process_info_dict = video_process_info.__dict__
        
        # Check if Redis is available before enqueueing
        try:
            redis_conn.ping()
        except Exception:
            logger.error("Redis server not responding - processing synchronously as fallback")
            video_info.status = ProcessingStatus.FAILED
            video_info.error = "Redis server not responding - processed synchronously"
            # Process synchronously as fallback
            ffmpeg_service = FfmpegService()
            ffmpeg_service.trim_video(video_info, video_process_info)
            return "no_queue_fallback"
            
        # Enqueue the job with args
        # On Windows, use a different way to specify timeout that doesn't depend on signals
        job_args = {
            'args': (video_info_dict, video_process_info_dict, chat_id),
            'result_ttl': 86400,  # Keep result for 24 hours
        }
        
        # Different timeout handling for Windows vs. Unix
        if platform.system() == 'Windows':
            # On Windows, don't use the timeout mechanism that depends on SIGALRM
            job = video_queue.enqueue(process_video_job, **job_args)
        else:
            # On Unix-like systems, you can use the built-in timeout
            job_args['job_timeout'] = '1h'  # 1 hour timeout
            job = video_queue.enqueue(process_video_job, **job_args)
        
        logger.info(f"Enqueued video processing job with ID: {job.id} for file ID: {video_info.file_id}")
        return job.id
    
    except Exception as e:
        logger.error(f"Error enqueueing video processing job: {str(e)}")
        # Process synchronously as fallback
        logger.info(f"Processing video synchronously as fallback due to queue error")
        video_info.status = ProcessingStatus.PROCESSING
        ffmpeg_service = FfmpegService()
        ffmpeg_service.trim_video(video_info, video_process_info)
        return "exception_fallback"

# Get job status
def get_job_status(job_id):
    """
    Get the status of a job by ID
    
    Args:
        job_id: RQ Job ID
    
    Returns:
        Job status and result if available
    """
    global redis_conn
    
    # Handle fallback job IDs
    if job_id in ["no_queue_fallback", "exception_fallback"]:
        return {
            'status': 'fallback_completed',
            'message': 'Job was processed synchronously due to Redis unavailability',
            'result': None
        }
    
    try:
        # Ensure Redis connection
        if redis_conn is None:
            redis_conn = get_redis_connection()
            
        if redis_conn is None:
            return {
                'status': 'error',
                'message': 'Redis connection unavailable'
            }
            
        # Try to ping Redis before proceeding
        try:
            redis_conn.ping()
        except Exception:
            return {
                'status': 'error',
                'message': 'Redis server not responding'
            }
            
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.get_status()
        
        result = None
        if status == 'finished':
            result = job.result
        
        return {
            'status': status,
            'result': result
        }
    
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        } 