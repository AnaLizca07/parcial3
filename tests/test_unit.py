import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from app.database import Base
from app.models import Producto, Categoria, Movimientos
from app.schemas import ProductoCreate, MovimientosCreate
import os

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:19951230@localhost:5432/parcial_test")
engine = create_engine(
    TEST_DATABASE_URL
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def producto_ejemplo(db_session):
    producto = Producto(
        nombre="Producto test",
        precio=100000,
        stock=20
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)
    return producto


def test_stock_increase_on_entrada(db_session, producto_ejemplo):
    estock_inicial = producto_ejemplo.stock
    movimiento = MovimientosCreate(
        producto_id=producto_ejemplo.id,
        cantidad=5,
        tipo="entrada"
    )
    
    response = client.post("/movimientos/", json=movimiento.model_dump())
    assert response.status_code == 201
    
    db_session.refresh(producto_ejemplo)
    assert producto_ejemplo.stock == estock_inicial + 5

def test_stock_decrease_on_salida(db_session, producto_ejemplo):
 
    estock_inicial = producto_ejemplo.stock
    movimiento = MovimientosCreate(
        producto_id=producto_ejemplo.id,
        cantidad=5,
        tipo="salida"
    )
    
    response = client.post("/movimientos/", json=movimiento.model_dump())
    assert response.status_code == 201
    
    db_session.refresh(producto_ejemplo)
    assert producto_ejemplo.stock == estock_inicial - 5

def test_insufficient_stock_error(db_session, producto_ejemplo):
    movimiento = MovimientosCreate(
        producto_id=producto_ejemplo.id,
        cantidad=producto_ejemplo.stock + 1,  
        tipo="salida"
    )
    
    response = client.post("/movimientos/", json=movimiento.model_dump())
    assert response.status_code == 400
    assert "No hay suficiente stock" in response.json()["detail"]


def test_product_required_fields():

    producto_incompleto = {
        "nombre": "Test Product"
    }
    
    response = client.post("/productos/", json=producto_incompleto)
    assert response.status_code == 422  

def test_movement_type_validation():
    movimiento_invalido = {
        "producto_id": 1,
        "cantidad": 5,
        "tipo": "tipo_invalido"  
    }
    
    response = client.post("/movimientos/", json=movimiento_invalido)
    assert response.status_code == 422  
