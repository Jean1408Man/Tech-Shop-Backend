from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.resumen import ProductoResumen


class CategoriaBase(BaseModel):
    nombre: str
    url_img: Optional[str] = None
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    url_img: Optional[str] = None
    descripcion: Optional[str] = None


class Categoria(CategoriaBase):
    id: int
    productos: List[ProductoResumen] = Field(default_factory=list)

    class Config:
        from_attributes = True
