from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import Enum as SQLEnum

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), index=True)
    stock = Column(Integer, default=0)

    categoria = relationship("Categoria", back_populates="productos")
    movimientos = relationship("Movimientos", back_populates="producto")

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, index=True)

    productos = relationship("Producto", back_populates="categoria")

class Movimientos(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), index=True)
    cantidad = Column(Integer, index=True)
    tipo = Column(SQLEnum("entrada", "salida", name="tipo_movimiento"), index=True)

    producto = relationship("Producto", back_populates="movimientos")
