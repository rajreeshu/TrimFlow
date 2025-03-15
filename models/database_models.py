from sqlalchemy import Column, Integer, String, BigInteger, Text, JSON, TIMESTAMP, Interval, ForeignKey, ARRAY, LargeBinary
from sqlalchemy.sql import func
from config.database import Base

class OriginalVideo(Base):
    __tablename__ = "original_video"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    location = Column(Text)
    size = Column(BigInteger)
    video_metadata = Column(JSON)
    created_date = Column(TIMESTAMP(timezone=True), default=func.now())
    created_user = Column(String(255))
    description = Column(Text)
    category = Column(String(255))
    remark = Column(Text)
    addon = Column(JSON)



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