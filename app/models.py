from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from .database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index=True)
    prompt = Column(Text)
    status = Column(String, default="created")  # created | pending | processing | done | failed
    created_at = Column(DateTime, default=datetime.utcnow)
    result_url = Column(Text, nullable=True)
    fal_job_id = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
