from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryIngest


async def create(db: AsyncSession, node_id: int, data: TelemetryIngest) -> Telemetry:
    record = Telemetry(node_id=node_id, **data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_by_node(db: AsyncSession, node_id: int, limit: int = 100) -> List[Telemetry]:
    result = await db.execute(
        select(Telemetry)
        .where(Telemetry.node_id == node_id)
        .order_by(Telemetry.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
