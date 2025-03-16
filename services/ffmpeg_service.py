import os
import subprocess
import logging

from fastapi import HTTPException

from config.config import properties
from models.video_models import ProcessingStatus, VideoInfo

logger = logging.getLogger(__name__)

class FfmpegService:
    def trim_video(self,video_info: VideoInfo) -> VideoInfo:
        """Trim the video into segments using FFmpeg."""
        try:
            video_info.status = ProcessingStatus.PROCESSING

            base_name = os.path.splitext(os.path.basename(video_info.filename))[0]
            output_pattern = os.path.join(properties.TRIMMED_DIR, f"{base_name}_{video_info.file_id}_part_%02d.mp4")

            # FFmpeg command to split video
            command = [
                "ffmpeg",
                "-i", video_info.original_path,
                "-c", "copy",  # Copy codec to speed up processing
                "-map", "0",
                "-segment_time", str(properties.SEGMENT_TIME),
                "-f", "segment",
                "-reset_timestamps", "1",
                output_pattern
            ]

            logger.info(f"Starting FFmpeg process for {video_info.filename}")
            process = subprocess.run(command, check=True, capture_output=True, text=True)

            # Get list of created segments
            segment_files = [f for f in os.listdir(properties.TRIMMED_DIR)
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

    def remove_metadata(self, file_path: str) -> str:
        """Remove all metadata from the video file."""
        base, ext = os.path.splitext(file_path)
        cleaned_file_path = f"{base}_cleaned{ext}"
        command = [
            "ffmpeg",
            "-i", file_path,
            "-map", "0:v",  # Map only the video stream
            "-map", "0:a",  # Map only the audio stream
            "-c", "copy",
            "-map_metadata", "-1",  # Remove all metadata
            cleaned_file_path
        ]

        try:
            logger.info(f"Removing metadata from {file_path}")
            subprocess.run(command, check=True)
            logger.info(f"Metadata removed, saved to {cleaned_file_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error removing metadata from {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to remove metadata: {str(e)}")

        return cleaned_file_path