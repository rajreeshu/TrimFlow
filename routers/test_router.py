import redis
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form

class TestRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/test", tags=["test"])
        self.add_routes()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def add_routes(self):
        @self.router.get("/enqueue/{text}")
        def get_video_status(
               text : str,
        ):
            self.redis_client.lpush('video_status_queue', text)
            return {"message": "Text added to queue", "text": text}
