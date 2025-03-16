import logging
import subprocess
import srt
import subprocess

logger = logging.getLogger(__name__)


def get_subtitle_from_video(video_path, track_index=0):
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-map', f'0:s:{track_index}',
            '-f', 'srt',
            'pipe:1'
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        subtitle_data = result.stdout.decode('utf-8')
        return subtitle_data
    except subprocess.CalledProcessError as e:
        print(f"Error extracting subtitles: {e.stderr.decode('utf-8')}")
        return None

def find_first_dialogue(subtitle_data):
    try:
        subtitles = list(srt.parse(subtitle_data))
        for subtitle in subtitles:
            if len(subtitle.content.strip()) > 3:
                return str(subtitle.start)
        return None
    except srt.SRTParseError as e:
        print(f"Error parsing subtitle data: {e}")
        return None


def find_movie_start_time(video_path):
    subtitle_data = get_subtitle_from_video(video_path)
    if subtitle_data:
        movie_start_time = find_first_dialogue(subtitle_data)
        if movie_start_time:
            print(f"Movie starts at: {movie_start_time}")
            return movie_start_time
        else:
            print("Could not determine movie start time.")
            return None
    else:
        print("No subtitles found.")
        return None
