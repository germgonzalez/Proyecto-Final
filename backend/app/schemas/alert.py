from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.alert import AlertType, AlertSeverity


class AlertCreate(BaseModel):
    node_id: int
    alert_type: AlertType
    severity: AlertSeverity
    message: str


class AlertResponse(BaseModel):
    id: int
    node_id: int
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
