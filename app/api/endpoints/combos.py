from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.core.database import get_db
from app.services.combo import ComboService
from app.use_cases.combos.commands import (
    CreateComboCommand,
    DeleteComboCommand,
    UpdateComboCommand,
)
from app.use_cases.combos.queries import GetComboByIdQuery, ListCombosQuery

router = APIRouter()


@router.post("/", response_model=schemas.Combo, status_code=201)
def create_combo(combo: schemas.ComboCreate, db: Session = Depends(get_db)):
    """Create a new combo."""
    try:
        return CreateComboCommand(
            nombre=combo.nombre,
            descripcion=combo.descripcion,
            precio=combo.precio,
            imagen=combo.imagen,
            producto_ids=combo.producto_ids,
            service=ComboService(db),
        ).execute()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/", response_model=List[schemas.Combo])
def read_combos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of combos."""
    return ListCombosQuery(
        service=ComboService(db),
        skip=skip,
        limit=limit,
    ).execute()


@router.get("/{combo_id}", response_model=schemas.Combo)
def read_combo(combo_id: int, db: Session = Depends(get_db)):
    """Get a specific combo by ID."""
    combo = GetComboByIdQuery(combo_id=combo_id, service=ComboService(db)).execute()
    if not combo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combo no encontrado.",
        )
    return combo


@router.put("/{combo_id}", response_model=schemas.Combo)
def update_combo(
    combo_id: int,
    combo_in: schemas.ComboUpdate,
    db: Session = Depends(get_db),
):
    """Update a combo by ID."""
    service = ComboService(db)
    combo = GetComboByIdQuery(combo_id=combo_id, service=service).execute()
    if not combo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combo no encontrado.",
        )

    try:
        return UpdateComboCommand(
            combo=combo,
            service=service,
            fields=combo_in.model_dump(exclude_unset=True),
        ).execute()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{combo_id}", response_model=schemas.Combo)
def delete_combo(combo_id: int, db: Session = Depends(get_db)):
    """Delete a combo by ID."""
    service = ComboService(db)
    combo = GetComboByIdQuery(combo_id=combo_id, service=service).execute()
    if not combo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combo no encontrado.",
        )
    return DeleteComboCommand(combo=combo, service=service).execute()
