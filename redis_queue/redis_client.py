import redis

from config.config import config_properties as properties
from typing import Optional

class RedisManager:
    __client: Optional[redis.Redis] = None

    def __init__(self) -> None:
        raise RuntimeError("Use get_client() instead")

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls.__client is None:
            try:
                cls.__client = redis.Redis(
                    host=properties.BASE_URL,
                    port=properties.REDIS_PORT,
                    decode_responses=True,
                    socket_timeout=5,  # Connection timeout
                    retry_on_timeout=True
                )
                # Test connection
                cls.__client.ping()
            except redis.ConnectionError as e:
                raise RuntimeError(f"Failed to connect to Redis: {str(e)}")
        return cls.__client

    @classmethod
    def close(cls) -> None:
        if cls.__client is not None:
            cls.__client.close()
            cls.__client = None