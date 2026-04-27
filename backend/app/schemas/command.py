from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.command import CommandType, CommandStatus


class CommandCreate(BaseModel):
    command_type: CommandType
    payload: Optional[dict] = None
    created_by: Optional[str] = None


class CommandAck(BaseModel):
    status: CommandStatus
    executed_at: Optional[datetime] = None


class CommandResponse(BaseModel):
    id: int
    node_id: int
    command_type: CommandType
    payload: Optional[dict] = None
    status: CommandStatus
    created_by: Optional[str] = None
    created_at: datetime
    executed_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
