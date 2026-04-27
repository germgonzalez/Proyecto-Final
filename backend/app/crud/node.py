from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate


async def get_by_device_code(db: AsyncSession, device_code: str) -> Optional[Node]:
    result = await db.execute(select(Node).where(Node.device_code == device_code))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, node_id: int) -> Optional[Node]:
    result = await db.execute(select(Node).where(Node.id == node_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> List[Node]:
    result = await db.execute(select(Node).order_by(Node.name))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: NodeCreate) -> Node:
    node = Node(**data.model_dump())
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node


async def update(db: AsyncSession, node: Node, data: NodeUpdate) -> Node:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(node, field, value)
    await db.commit()
    await db.refresh(node)
    return node


async def update_last_seen(
    db: AsyncSession,
    node: Node,
    latitude: Optional[float],
    longitude: Optional[float],
) -> None:
    node.last_seen = datetime.now(timezone.utc)
    if latitude is not None:
        node.latitude = latitude
    if longitude is not None:
        node.longitude = longitude
    await db.commit()
