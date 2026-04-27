import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CommandType(str, enum.Enum):
    set_dimming = "set_dimming"
    turn_on = "turn_on"
    turn_off = "turn_off"


class CommandStatus(str, enum.Enum):
    pending = "pending"
    executed = "executed"
    failed = "failed"


class Command(Base):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False, index=True)
    command_type = Column(SAEnum(CommandType), nullable=False)
    payload = Column(JSON, nullable=True)
    status = Column(SAEnum(CommandStatus), default=CommandStatus.pending, nullable=False)
    created_by = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    node = relationship("Node", back_populates="commands")
