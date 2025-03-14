import os
import subprocess
import logging
from config.config import settings
from models.video_models import ProcessingStatus, VideoInfo

logger = logging.getLogger(__name__)

def trim_video(video_info: VideoInfo) -> VideoInfo:
    """Trim the video into segments using FFmpeg."""
    try:
        video_info.status = ProcessingStatus.PROCESSING
        
        base_name = os.path.splitext(os.path.basename(video_info.filename))[0]
        output_pattern = os.path.join(settings.TRIMMED_DIR, f"{base_name}_{video_info.file_id}_part_%02d.mp4")
        
        # FFmpeg command to split video
        command = [
            "ffmpeg",
            "-i", video_info.original_path,
            "-c", "copy",  # Copy codec to speed up processing
            "-map", "0",
            "-segment_time", str(settings.SEGMENT_TIME),
            "-f", "segment",
            "-reset_timestamps", "1",
            output_pattern
        ]
        
        logger.info(f"Starting FFmpeg process for {video_info.filename}")
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Get list of created segments
        segment_files = [f for f in os.listdir(settings.TRIMMED_DIR) 
                         if f.startswith(f"{base_name}_{video_info.file_id}_part_")]
        video_info.segments = sorted(segment_files)
        video_info.status = ProcessingStatus.COMPLETED
        
        logger.info(f"Video trimming completed for {video_info.filename}")
        return video_info
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error for {video_info.filename}: {e.stderr}")
        video_info.status = ProcessingStatus.FAILED
        video_info.error = f"FFmpeg error: {e.stderr}"
        return video_info
    except Exception as e:
        logger.error(f"Error processing {video_info.filename}: {str(e)}")
        video_info.status = ProcessingStatus.FAILED
        video_info.error = f"Processing error: {str(e)}"
        return video_info
