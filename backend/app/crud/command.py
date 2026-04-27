from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.command import Command, CommandStatus
from app.schemas.command import CommandCreate


async def create(db: AsyncSession, node_id: int, data: CommandCreate) -> Command:
    command = Command(node_id=node_id, **data.model_dump())
    db.add(command)
    await db.commit()
    await db.refresh(command)
    return command


async def get_pending(db: AsyncSession, node_id: int) -> List[Command]:
    result = await db.execute(
        select(Command)
        .where(Command.node_id == node_id, Command.status == CommandStatus.pending)
        .order_by(Command.created_at)
    )
    return list(result.scalars().all())


async def acknowledge(
    db: AsyncSession,
    command: Command,
    status: CommandStatus,
    executed_at: Optional[datetime] = None,
) -> Command:
    command.status = status
    command.acknowledged_at = datetime.now(timezone.utc)
    command.executed_at = executed_at or datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(command)
    return command
