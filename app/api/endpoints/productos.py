from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.core.database import get_db
from app.services.producto import ProductoService
from app.use_cases.productos.commands import (
    CreateProductoCommand,
    DeleteProductoCommand,
    UpdateProductoCommand,
)
from app.use_cases.productos.queries import GetProductoByIdQuery, ListProductosQuery

router = APIRouter()


@router.post("/", response_model=schemas.Producto, status_code=201)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    return CreateProductoCommand(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio_base=producto.precio_base,
        url_img=producto.url_img,
        service=ProductoService(db),
    ).execute()


@router.get("/", response_model=List[schemas.Producto])
def read_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of products."""
    return ListProductosQuery(
        service=ProductoService(db),
        skip=skip,
        limit=limit,
    ).execute()


@router.get("/{producto_id}", response_model=schemas.Producto)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    producto = GetProductoByIdQuery(
        producto_id=producto_id,
        service=ProductoService(db),
    ).execute()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado.",
        )
    return producto


@router.put("/{producto_id}", response_model=schemas.Producto)
def update_producto(
    producto_id: int,
    producto_in: schemas.ProductoUpdate,
    db: Session = Depends(get_db),
):
    """Update a product by ID."""
    service = ProductoService(db)
    producto = GetProductoByIdQuery(producto_id=producto_id, service=service).execute()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado.",
        )
    return UpdateProductoCommand(
        producto=producto,
        service=service,
        fields=producto_in.model_dump(exclude_unset=True),
    ).execute()


@router.delete("/{producto_id}", response_model=schemas.Producto)
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID."""
    service = ProductoService(db)
    producto = GetProductoByIdQuery(producto_id=producto_id, service=service).execute()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado.",
        )
    return DeleteProductoCommand(producto=producto, service=service).execute()
