from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    device_code = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(256), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    installed_at = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    telemetry = relationship("Telemetry", back_populates="node", lazy="select")
    commands = relationship("Command", back_populates="node", lazy="select")
    alerts = relationship("Alert", back_populates="node", lazy="select")
