from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

    voltage = Column(Float, nullable=True)       # V
    current = Column(Float, nullable=True)        # A
    power = Column(Float, nullable=True)          # W
    power_factor = Column(Float, nullable=True)   # 0.0 - 1.0
    dimming_level = Column(Integer, nullable=True)  # 0 - 100 %
    is_on = Column(Boolean, nullable=True)
    status_ok = Column(Boolean, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    node = relationship("Node", back_populates="telemetry")
