from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app import models, schemas
from app.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventario de productos espectaculares jeje")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, DELETE, etc.
    allow_headers=["*"],  # Permite todos los headers
)

static_dir = "app/static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Root"])
def read_root():
    try:
        return FileResponse('app/index.html')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index file not found")


#endpont pa verificar la salud de la api
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "message": "Application is running"}


#primero los endpoints del crud de productos
@app.post("/productos/", response_model=schemas.ProductoResponse, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_producto = models.Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.get("/productos/", response_model=List[schemas.ProductoResponse], tags=["Productos"])
def leer_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).offset(skip).limit(limit).all()
    return productos

@app.get("/productos/{producto_id}", response_model=schemas.ProductoDetailResponse, tags=["Productos"])
def leer_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="No se encuentra ese producto :(")
    return producto

@app.put("/productos/{producto_id}", response_model=schemas.ProductoResponse, tags=["Productos"])
def actualizar_producto(producto_id: int, producto: schemas.ProductoUpdate, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="No se encuentra ese producto :(")
    
    update_data = producto.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_producto, field, value)
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="No se encuentra ese producto :(")
    db.delete(producto)
    db.commit()
    return None


#aqui ya empiezan los endpoints del crdud de categorias
@app.post("/categorias/", response_model=schemas.CategoriaResponse, status_code=status.HTTP_201_CREATED, tags=["Categorías"])
def crear_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = models.Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.get("/categorias/", response_model=List[schemas.CategoriaResponse], tags=["Categorías"])
def leer_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).offset(skip).limit(limit).all()
    return categorias

@app.get("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse, tags=["Categorías"])
def leer_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="No se encuentra esa categoría :(")
    return categoria

@app.put("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse, tags=["Categorías"])
def actualizar_categoria(categoria_id: int, categoria: schemas.CategoriaUpdate, db: Session = Depends(get_db)):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="No se encuentra esa categoría :(")
    
    update_data = categoria.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_categoria, field, value)
    
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.delete("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Categorías"])
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="No se encuentra esa categoría :(")
    db.delete(categoria)
    db.commit()
    return None


#crud para los movimientoss del stock
@app.post("/movimientos/", response_model=schemas.MovimientosResponse, status_code=status.HTTP_201_CREATED, tags=["Stock"])
def crear_movimiento(movimiento: schemas.MovimientosCreate, db: Session = Depends(get_db)):

    producto = db.query(models.Producto).filter(models.Producto.id == movimiento.producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="No se encuentra ese producto :(")
    
    if movimiento.tipo == "entrada":
        producto.stock += movimiento.cantidad
    else:  
        if producto.stock < movimiento.cantidad:
            raise HTTPException(status_code=400, detail="No hay suficiente stock pa esto")
        producto.stock -= movimiento.cantidad

    db_movimiento = models.Movimientos(**movimiento.model_dump())
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento

@app.get("/movimientos/", response_model=List[schemas.MovimientosResponse], tags=["Stock"])
def leer_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movimientos = db.query(models.Movimientos).offset(skip).limit(limit).all()
    return movimientos

@app.get("/reportes/bajo-stock/", response_model=List[schemas.ProductoResponse], tags=["Reportes"])
def gtraer_productos_menor_diez(db: Session = Depends(get_db)):
    productos = db.query(models.Producto).filter(models.Producto.stock < 10).all()
    return productos

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
