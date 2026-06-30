from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.database import get_db
from app.services.pedido import PedidoService
from app.use_cases.pedidos.commands import (
    CreatePedidoCommand,
    DeletePedidoCommand,
    UpdatePedidoCommand,
)
from app.use_cases.pedidos.queries import GetPedidoByIdQuery, ListPedidosQuery

router = APIRouter()


@router.post("/", response_model=schemas.Pedido, status_code=201)
def create_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    try:
        return CreatePedidoCommand(
            nombre=pedido.nombre,
            telefono=pedido.telefono,
            productos=[item.model_dump() for item in pedido.productos],
            combos=[item.model_dump() for item in pedido.combos],
            service=PedidoService(db),
        ).execute()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/", response_model=List[schemas.Pedido])
def read_pedidos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of orders."""
    return ListPedidosQuery(
        service=PedidoService(db),
        skip=skip,
        limit=limit,
    ).execute()


@router.get("/{pedido_id}", response_model=schemas.Pedido)
def read_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID."""
    pedido = GetPedidoByIdQuery(pedido_id=pedido_id, service=PedidoService(db)).execute()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado.",
        )
    return pedido


@router.put("/{pedido_id}", response_model=schemas.Pedido)
def update_pedido(
    pedido_id: int,
    pedido_in: schemas.PedidoUpdate,
    db: Session = Depends(get_db),
):
    """Update an order by ID."""
    service = PedidoService(db)
    pedido = GetPedidoByIdQuery(pedido_id=pedido_id, service=service).execute()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado.",
        )

    fields = pedido_in.model_dump(exclude_unset=True)
    if "productos" in fields and fields["productos"] is not None:
        fields["productos"] = [item.model_dump() for item in pedido_in.productos or []]
    if "combos" in fields and fields["combos"] is not None:
        fields["combos"] = [item.model_dump() for item in pedido_in.combos or []]

    try:
        return UpdatePedidoCommand(
            pedido=pedido,
            service=service,
            fields=fields,
        ).execute()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{pedido_id}", response_model=schemas.Pedido)
def delete_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Delete an order by ID."""
    service = PedidoService(db)
    pedido = GetPedidoByIdQuery(pedido_id=pedido_id, service=service).execute()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado.",
        )
    return DeletePedidoCommand(pedido=pedido, service=service).execute()
