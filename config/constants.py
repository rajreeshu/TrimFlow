

# redis constants
REDIS_VIDEO_QUEUE_NAME : str = "video_processing_queue"
REDIS_VIDEO_PROCESSING_COMPLETED_QUEUE_NAME : str= "video_processing_completed"


# Common Terms
LANDSCAPE :str = "landscape"
PORTRAIT : str = "portrait"
IMAGE : str = "image"
VIDEO :str = "video"

# Default values
DEFAULT_VIDEO_SEGMENT_TIME : int = 55  # seconds
DEFAULT_START_TIME : int = 0  # seconds
DEFAULT_END_TIME : int = 0  # seconds