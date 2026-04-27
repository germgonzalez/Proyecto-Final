from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.deps import get_db_session
from app.crud import node as node_crud
from app.schemas.node import NodeCreate, NodeResponse, NodeUpdate

router = APIRouter()


@router.get("/", response_model=List[NodeResponse])
async def list_nodes(db: AsyncSession = Depends(get_db_session)):
    return await node_crud.get_all(db)


@router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(data: NodeCreate, db: AsyncSession = Depends(get_db_session)):
    existing = await node_crud.get_by_device_code(db, data.device_code)
    if existing:
        raise HTTPException(status_code=400, detail="device_code ya registrado")
    return await node_crud.create(db, data)


@router.get("/{device_code}", response_model=NodeResponse)
async def get_node(device_code: str, db: AsyncSession = Depends(get_db_session)):
    node = await node_crud.get_by_device_code(db, device_code)
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return node


@router.patch("/{device_code}", response_model=NodeResponse)
async def update_node(
    device_code: str,
    data: NodeUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    node = await node_crud.get_by_device_code(db, device_code)
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return await node_crud.update(db, node, data)
