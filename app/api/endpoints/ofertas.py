from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.core.database import get_db
from app.services.oferta import OfertaService
from app.use_cases.ofertas.commands import (
    CreateOfertaCommand,
    DeleteOfertaCommand,
    UpdateOfertaCommand,
)
from app.use_cases.ofertas.queries import GetOfertaByIdQuery, ListOfertasQuery

router = APIRouter()


@router.post("/", response_model=schemas.Oferta, status_code=201)
def create_oferta(oferta: schemas.OfertaCreate, db: Session = Depends(get_db)):
    """Create a new offer."""
    try:
        return CreateOfertaCommand(
            fecha_inicio=oferta.fecha_inicio,
            fecha_fin=oferta.fecha_fin,
            nombre=oferta.nombre,
            descripcion=oferta.descripcion,
            monto_descuento=oferta.monto_descuento,
            producto_ids=oferta.producto_ids,
            service=OfertaService(db),
        ).execute()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/", response_model=List[schemas.Oferta])
def read_ofertas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of offers."""
    return ListOfertasQuery(
        service=OfertaService(db),
        skip=skip,
        limit=limit,
    ).execute()


@router.get("/{oferta_id}", response_model=schemas.Oferta)
def read_oferta(oferta_id: int, db: Session = Depends(get_db)):
    """Get a specific offer by ID."""
    oferta = GetOfertaByIdQuery(oferta_id=oferta_id, service=OfertaService(db)).execute()
    if not oferta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta no encontrada.",
        )
    return oferta


@router.put("/{oferta_id}", response_model=schemas.Oferta)
def update_oferta(
    oferta_id: int,
    oferta_in: schemas.OfertaUpdate,
    db: Session = Depends(get_db),
):
    """Update an offer by ID."""
    service = OfertaService(db)
    oferta = GetOfertaByIdQuery(oferta_id=oferta_id, service=service).execute()
    if not oferta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta no encontrada.",
        )

    try:
        return UpdateOfertaCommand(
            oferta=oferta,
            service=service,
            fields=oferta_in.model_dump(exclude_unset=True),
        ).execute()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{oferta_id}", response_model=schemas.Oferta)
def delete_oferta(oferta_id: int, db: Session = Depends(get_db)):
    """Delete an offer by ID."""
    service = OfertaService(db)
    oferta = GetOfertaByIdQuery(oferta_id=oferta_id, service=service).execute()
    if not oferta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta no encontrada.",
        )
    return DeleteOfertaCommand(oferta=oferta, service=service).execute()
