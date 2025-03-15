import subliminal
import pysrt
import logging
from babelfish import Language

logger = logging.getLogger(__name__)

def download_subtitle(movie_name):
    # Search for subtitles
    subtitles = subliminal.download_best_subtitles([subliminal.Video(movie_name)], {Language('eng')})
    
    # Save subtitles
    for video, subs in subtitles.items():
        subliminal.save_subtitles(video, subs)


def find_first_dialogue(srt_path):
    subs = pysrt.open(srt_path)
    for sub in subs:
        if len(sub.text.strip()) > 3:
            return str(sub.start)
    return None


def find_movie_start_time(movie_name):
    srt_file = download_subtitle(movie_name)
    if srt_file:
        movie_start_time = find_first_dialogue(srt_file)
        if movie_start_time:
            logging.info(f"Movie starts at: {movie_start_time}")
            return movie_start_time
        else:
            logging.info("Could not determine movie start time.")
            return None
    else:
        logging.info("Subtitle not found.")
        return None
