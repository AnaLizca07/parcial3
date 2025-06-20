from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from enum import Enum

class TipoMovimiento(str, Enum):
    entrada = "entrada"
    salida = "salida"

#schemas de los productos
class ProductoBase(BaseModel):
    id: Optional[int] = Field(default=None)
    nombre: str = Field(...)
    precio: float = Field(...)
    categoria_id: Optional[int] = Field(default=None)
    stock: int = Field(default=0)

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    id: int = Field(...)
    nombre: Optional[str] = Field(default=None)
    precio: Optional[float] = Field(default=None)
    categoria_id: Optional[int] = Field(default=None)

class ProductoResponse(ProductoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


#schemas de las categoriass
class CategoriaBase(BaseModel):
    nombre: str = Field(...)
    descripcion: str = Field(...)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None)
    descripcion: Optional[str] = Field(default=None)

class CategoriaResponse(CategoriaBase):
    id: int
    productos: List[ProductoResponse] = []
    model_config = ConfigDict(from_attributes=True)


#schemas de los movimientos
class MovimientosBase(BaseModel):
    producto_id: int = Field(...)
    cantidad: int = Field(...)
    tipo: TipoMovimiento = Field(...)

class MovimientosCreate(MovimientosBase):
    pass

class MovimientosUpdate(BaseModel):
    cantidad: Optional[int] = Field(default=None)
    tipo: Optional[TipoMovimiento] = Field(default=None)

class MovimientosResponse(MovimientosBase):
    id: int
    producto: ProductoResponse
    model_config = ConfigDict(from_attributes=True)


class ProductoDetailResponse(ProductoResponse):
    categoria: Optional[CategoriaBase] = None
    movimientos: List[MovimientosBase] = []
