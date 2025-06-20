import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from app.database import SessionLocal
from app.models import Producto, Categoria, Movimientos

import logging
from app import models

class TestInventorySystem:
    @pytest.fixture(scope="function")
    def driver(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    @pytest.fixture(scope="function")
    def db(self):
        db = SessionLocal()
        db.query(models.Movimientos).delete()
        db.query(models.Producto).delete()
        db.query(models.Categoria).delete()
        db.commit()
        yield db
        db.close()

    def test_create_product_api(self, driver, db):
        driver.get("http://localhost:8000")
        
        add_product_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Agregar Producto')]")
        add_product_tab.click()
        
        category_name = "Test Category"
        category_desc = "Test Description"
        
        driver.find_element(By.ID, "categoryName").send_keys(category_name)
        driver.find_element(By.ID, "categoryDescription").send_keys(category_desc)
        driver.find_element(By.XPATH, "//form[@id='categoryForm']//button").click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        time.sleep(2)

        driver.find_element(By.ID, "productName").send_keys("Test Product")
        driver.find_element(By.ID, "productPrice").send_keys("2000")

        category_select = Select(driver.find_element(By.ID, "productCategory"))
        category_select.select_by_visible_text(category_name)
        

        stock_input = driver.find_element(By.ID, "productStock")
        stock_input.clear()
        time.sleep(0.5)  
        stock_input.send_keys("2")
        time.sleep(0.5) 
        
        assert stock_input.get_attribute("value") == "2"
        

        submit_button = driver.find_element(By.XPATH, "//form[@id='productForm']//button")
        submit_button.click()
    
        time.sleep(2)
        
 
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "exitosamente" in success_alert.text
        
 
        product = db.query(Producto).filter(Producto.nombre == "Test Product").first()
        assert product is not None
        assert product.precio == 2000
        assert product.stock == 2


    def test_database_integration(self, db):

        category = Categoria(nombre="Test Category", descripcion="Test Description")
        db.add(category)
        db.commit()
        

        product = Producto(
            nombre="Integration Test Product",
            precio=2000,
            categoria_id=category.id,
            stock=2
        )
        db.add(product)
        db.commit()

        db.refresh(product)
        assert product.categoria.nombre == "Test Category"
        
   
        movement = Movimientos(
            producto_id=product.id,
            cantidad=5,
            tipo="entrada"
        )
        db.add(movement)
        db.commit()
        
       
        db.refresh(product)
        assert product.stock == 2

    def test_stock_update_flow(self, driver, db):

        driver.get("http://localhost:8000")

        add_product_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Agregar Producto')]")
        add_product_tab.click()
        

        driver.find_element(By.ID, "categoryName").send_keys("Test Category")
        driver.find_element(By.ID, "categoryDescription").send_keys("Test Description")
        driver.find_element(By.XPATH, "//form[@id='categoryForm']//button").click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        time.sleep(2)

        driver.find_element(By.ID, "productName").send_keys("E2E Test Product")
        driver.find_element(By.ID, "productPrice").send_keys("2000")
        
        stock_input = driver.find_element(By.ID, "productStock")
        stock_input.clear()
        stock_input.send_keys("2")  
        
        category_select = Select(driver.find_element(By.ID, "productCategory"))
        category_select.select_by_visible_text("Test Category")
        
        driver.find_element(By.XPATH, "//form[@id='productForm']//button").click()
        
    
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        time.sleep(3)


        stock_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Gestión de Stock')]")
        stock_tab.click()
        
        time.sleep(2)
   
        product_select = Select(driver.find_element(By.ID, "stockProduct"))
        

        WebDriverWait(driver, 10).until(
            lambda d: len(product_select.options) > 1
        )
        
        options = product_select.options
        for option in options:
            if "E2E Test Product" in option.text:
                product_select.select_by_value(option.get_attribute("value"))
                break
        else:
            raise Exception("Product option with 'E2E Test Product' not found in dropdown")
        
       
        driver.find_element(By.ID, "stockQuantity").send_keys("5")
        Select(driver.find_element(By.ID, "stockType")).select_by_value("entrada")
        driver.find_element(By.XPATH, "//form[@id='stockForm']//button").click()
        
  
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )

        driver.find_element(By.ID, "stockQuantity").clear()
        driver.find_element(By.ID, "stockQuantity").send_keys("12")
        Select(driver.find_element(By.ID, "stockType")).select_by_value("salida")
        driver.find_element(By.XPATH, "//form[@id='stockForm']//button").click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        low_stock_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Stock Bajo')]")
        low_stock_tab.click()
        time.sleep(3) 
        
        
        low_stock_products = driver.find_elements(By.CLASS_NAME, "product-card")
        product_found = False
        for product in low_stock_products:
            if "E2E Test Product" in product.text:
                product_found = True
      
                if "Requiere reposición urgente" not in product.text:
                    print("Warning: Low stock message not found in product card text")
                assert "Requiere reposición urgente" in product.text
                break
        
        assert product_found, "Product should appear in low stock report"
        
 
        product = db.query(Producto).filter(Producto.nombre == "E2E Test Product").first()
        assert product.stock == 7  
