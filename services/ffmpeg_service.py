import os
import subprocess
import logging

from fastapi import HTTPException

from config.config import config_properties
from models.video_models import ProcessingStatus, VideoInfo, VideoProcessInfo, VideoScreenType

from typing import List

logger = logging.getLogger(__name__)

class FfmpegService:
    # async def trim_video(self,video_info: VideoInfo,  skip_pairs: List[tuple], segment_time: int, start_time:int, end_time:int) -> VideoInfo:
    async def trim_video(self,video_info: VideoInfo,  video_process_info:VideoProcessInfo) -> VideoInfo:
        skip_pairs: List[tuple] = video_process_info.skip_pairs
        segment_time: int = video_process_info.segment_time
        start_time: int = video_process_info.start_time
        end_time: int = video_process_info.end_time
        orientation: VideoScreenType = video_process_info.screen_type

        """Trim the video into segments using FFmpeg."""
        try:
            # Get the duration of the video
            command_duration = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_info.original_path
            ]
            duration_result = subprocess.run(command_duration, check=True, capture_output=True, text=True)
            total_duration = float(duration_result.stdout.strip())

            # Adding in touples to remove the start and End time of the video
            skip_pairs.append((0, start_time))
            skip_pairs.append((total_duration-end_time, total_duration))

            video_info.status = ProcessingStatus.PROCESSING

            base_name = os.path.splitext(os.path.basename(video_info.filename))[0]
            output_pattern = os.path.join(config_properties.TRIMMED_DIR, f"{base_name}_{video_info.file_id}_part_%02d.mp4")

            scale_filter = ""
            pad_filter = ""
            if orientation is not None:
                # Get video dimensions
                command_dimensions = [
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "csv=s=x:p=0",
                    video_info.original_path
                ]
                dimensions_result = subprocess.run(command_dimensions, check=True, capture_output=True, text=True)
                width, height = map(int, dimensions_result.stdout.strip().split('x'))

                target_width = None
                target_height = None
                # Determine if rotation is needed
                if orientation == VideoScreenType.PORTRAIT and height < width:
                    target_width, target_height = config_properties.HEIGHT_720P, config_properties.WIDTH_720P
                elif orientation == VideoScreenType.LANDSCAPE and width < height:
                    target_width, target_height = config_properties.WIDTH_720P, config_properties.HEIGHT_720P

                if target_width is not None and target_height is not None:
                    # Create scale and pad filters
                    scale_filter = f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease"
                    pad_filter = f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
                else:
                    scale_filter = ""
                    pad_filter = ""

            # Create the select filter expression
            select_expr = " + ".join([f"between(t,{start},{end})" for start, end in skip_pairs])

            select_filter = f"select='not({select_expr})',setpts=N/FRAME_RATE/TB"
            filters = [select_filter]
            if scale_filter:
                filters.append(scale_filter)
            if pad_filter:
                filters.append(pad_filter)

            # Join the filters with commas
            filter_chain = ",".join(filters)

            # FFmpeg command to split video
            command = [
                "ffmpeg",
                "-i", video_info.original_path,
                 "-vf", filter_chain,
                "-af", f"aselect='not({select_expr})',asetpts=N/SR/TB",
                "-c:v", "libx264",  # Specify video codec
                "-c:a", "aac",  # Specify audio codec
                "-map", "0",
                "-segment_time", str(segment_time),
                "-f", "segment",
                "-reset_timestamps", "1",
                output_pattern
            ]

            logger.info(f"Starting FFmpeg process for {video_info.filename}")
            subprocess.run(command, check=True, capture_output=True, text=True)

            # Get list of created segments
            segment_files = [f for f in os.listdir(config_properties.TRIMMED_DIR)
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

        try:
            # Check if the input file has an audio stream
            probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of',
                         'csv=p=0', file_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            has_audio = bool(result.stdout.strip())

            # Construct the ffmpeg command
            command = ['ffmpeg', '-i', file_path, '-map', '0:v']
            if has_audio:
                command.extend(['-map', '0:a'])
            command.extend(['-c', 'copy', '-map_metadata', '-1', cleaned_file_path])

            logger.info(f"Removing metadata from {file_path}")
            subprocess.run(command, check=True)
            logger.info(f"Metadata removed, saved to {cleaned_file_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error removing metadata from {file_path}: {e}")

        return cleaned_file_path