import enum
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AlertType(str, enum.Enum):
    offline = "offline"
    voltage_high = "voltage_high"
    voltage_low = "voltage_low"
    power_high = "power_high"
    power_factor_low = "power_factor_low"
    lamp_failure = "lamp_failure"
    communication_error = "communication_error"


class AlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False, index=True)
    alert_type = Column(SAEnum(AlertType), nullable=False)
    severity = Column(SAEnum(AlertSeverity), nullable=False)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    node = relationship("Node", back_populates="alerts")
