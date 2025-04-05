from typing import Optional

from sqlalchemy import Column, Integer, String, BigInteger, Text, JSON, TIMESTAMP, Interval, ForeignKey, ARRAY, \
    LargeBinary
from sqlalchemy.sql import func

from database.database_config import Base


class OriginalVideo(Base):
    __tablename__ = "original_video"

    id: int = Column(Integer, primary_key=True, index=True)
    video_id: Optional[str] = Column(String(255), unique=True, nullable=False)
    name: str = Column(String(255))
    location: str = Column(Text)
    size: Optional[int] = Column(BigInteger)
    video_metadata: dict = Column(JSON)
    created_date: str = Column(TIMESTAMP(timezone=True), default=func.now())
    created_user: str = Column(String(255))
    description: str = Column(Text)
    category: str = Column(String(255))

    remark: str = Column(Text)
    addon: dict = Column(JSON)


class TrimmedVideo(Base):
    __tablename__ = 'trimmed_videos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_video_id = Column(Integer, ForeignKey('original_video.id'), nullable=False)
    start_time = Column(Interval, nullable=False)
    end_time = Column(Interval, nullable=False)
    remark = Column(Text, nullable=True)
    created_time = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')
    updated_time = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')
    description = Column(Text, nullable=True)
    hashtags = Column(ARRAY(Text), nullable=True)
    thumbnail = Column(LargeBinary, nullable=True)
    file_name = Column(Text, nullable=False)
    location = Column(Text, nullable=False)