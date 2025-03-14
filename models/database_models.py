from sqlalchemy import Column, Integer, String, BigInteger, Text, JSON, TIMESTAMP
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
