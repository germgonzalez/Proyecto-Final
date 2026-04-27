from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.deps import get_db_session
from app.crud import node as node_crud, command as command_crud
from app.schemas.command import CommandCreate, CommandResponse, CommandAck
from app.models.command import Command

router = APIRouter()


@router.get("/{device_code}/commands/pending", response_model=List[CommandResponse])
async def get_pending_commands(
    device_code: str,
    db: AsyncSession = Depends(get_db_session),
):
    node = await node_crud.get_by_device_code(db, device_code)
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return await command_crud.get_pending(db, node.id)


@router.post("/{device_code}/commands", response_model=CommandResponse, status_code=status.HTTP_201_CREATED)
async def send_command(
    device_code: str,
    data: CommandCreate,
    db: AsyncSession = Depends(get_db_session),
):
    node = await node_crud.get_by_device_code(db, device_code)
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return await command_crud.create(db, node.id, data)


@router.post("/{device_code}/commands/{command_id}/ack", response_model=CommandResponse)
async def acknowledge_command(
    device_code: str,
    command_id: int,
    data: CommandAck,
    db: AsyncSession = Depends(get_db_session),
):
    node = await node_crud.get_by_device_code(db, device_code)
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    result = await db.execute(
        select(Command).where(Command.id == command_id, Command.node_id == node.id)
    )
    command = result.scalar_one_or_none()
    if not command:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    return await command_crud.acknowledge(db, command, data.status, data.executed_at)
