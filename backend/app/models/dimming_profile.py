from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class DimmingProfile(Base):
    __tablename__ = "dimming_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    # Lista de entradas: [{"time": "20:00", "dimming": 100}, {"time": "23:00", "dimming": 50}, ...]
    schedule = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
