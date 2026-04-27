from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ScheduleEntry(BaseModel):
    time: str   # "HH:MM"
    dimming: int  # 0 - 100


class DimmingProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    schedule: List[ScheduleEntry]


class DimmingProfileResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    schedule: List[ScheduleEntry]
    created_at: datetime

    model_config = {"from_attributes": True}
