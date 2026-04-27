from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NodeCreate(BaseModel):
    device_code: str
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    installed_at: Optional[datetime] = None
    is_active: bool = True


class NodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class NodeResponse(BaseModel):
    id: int
    device_code: str
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool
    installed_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
