from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.database import get_db
from app.services.categoria import CategoriaService
from app.use_cases.categorias.commands import (
    CreateCategoriaCommand,
    DeleteCategoriaCommand,
    UpdateCategoriaCommand,
)
from app.use_cases.categorias.queries import (
    GetCategoriaByIdQuery,
    ListCategoriasQuery,
)

router = APIRouter()


@router.post("/", response_model=schemas.Categoria, status_code=201)
def create_categoria(
    categoria: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
):
    """Create a new category."""
    return CreateCategoriaCommand(
        nombre=categoria.nombre,
        url_img=categoria.url_img,
        descripcion=categoria.descripcion,
        service=CategoriaService(db),
    ).execute()


@router.get("/", response_model=List[schemas.Categoria])
def read_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of categories."""
    return ListCategoriasQuery(
        service=CategoriaService(db),
        skip=skip,
        limit=limit,
    ).execute()


@router.get("/{categoria_id}", response_model=schemas.Categoria)
def read_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    categoria = GetCategoriaByIdQuery(
        categoria_id=categoria_id,
        service=CategoriaService(db),
    ).execute()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria no encontrada.",
        )
    return categoria


@router.put("/{categoria_id}", response_model=schemas.Categoria)
def update_categoria(
    categoria_id: int,
    categoria_in: schemas.CategoriaUpdate,
    db: Session = Depends(get_db),
):
    """Update a category by ID."""
    service = CategoriaService(db)
    categoria = GetCategoriaByIdQuery(
        categoria_id=categoria_id,
        service=service,
    ).execute()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria no encontrada.",
        )
    return UpdateCategoriaCommand(
        categoria=categoria,
        service=service,
        fields=categoria_in.model_dump(exclude_unset=True),
    ).execute()


@router.delete("/{categoria_id}", response_model=schemas.Categoria)
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Delete a category by ID."""
    service = CategoriaService(db)
    categoria = GetCategoriaByIdQuery(
        categoria_id=categoria_id,
        service=service,
    ).execute()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria no encontrada.",
        )

    try:
        return DeleteCategoriaCommand(categoria=categoria, service=service).execute()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
