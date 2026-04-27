from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TelemetryIngest(BaseModel):
    timestamp: datetime
    voltage: Optional[float] = None
    current: Optional[float] = None
    power: Optional[float] = None
    power_factor: Optional[float] = None
    dimming_level: Optional[int] = None
    is_on: Optional[bool] = None
    status_ok: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TelemetryResponse(TelemetryIngest):
    id: int
    node_id: int
    received_at: datetime

    model_config = {"from_attributes": True}
