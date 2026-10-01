"""
Funciones auxiliares para las pruebas de saucedemo.com.

Acá se concentra todo lo que se repite entre los tests:
- Leer los datos de prueba del archivo JSON (carpeta datos/).
- Crear y configurar el WebDriver de Chrome.
- Hacer el login con esperas explícitas.
- Leer el nombre y precio de un producto.
- Guardar capturas de pantalla (se usan cuando un test falla).

Así los archivos de tests quedan cortos y fáciles de leer.
"""

import json
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---------------------------------------------------------------------------
# Rutas del proyecto (se calculan a partir de la ubicación de este archivo)
# ---------------------------------------------------------------------------
CARPETA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATOS = os.path.join(CARPETA_RAIZ, "datos", "datos_prueba.json")
CARPETA_CAPTURAS = os.path.join(CARPETA_RAIZ, "reports", "capturas")

# ---------------------------------------------------------------------------
# Localizadores (tuplas: estrategia + selector)
# Regla de oro de la Clase 8: ID -> Name -> CSS corto -> XPath solo si hace falta
# ---------------------------------------------------------------------------
# Página de login
CAMPO_USUARIO = (By.ID, "user-name")
CAMPO_CLAVE = (By.ID, "password")
BOTON_LOGIN = (By.ID, "login-button")

# Página de inventario
TITULO_SECCION = (By.CSS_SELECTOR, "div.header_secondary_container .title")
TARJETAS_PRODUCTO = (By.CLASS_NAME, "inventory_item")
NOMBRE_PRODUCTO = (By.CLASS_NAME, "inventory_item_name")
PRECIO_PRODUCTO = (By.CLASS_NAME, "inventory_item_price")
BOTON_MENU = (By.ID, "react-burger-menu-btn")
FILTRO_ORDEN = (By.CSS_SELECTOR, "select.product_sort_container")
ICONO_CARRITO = (By.CLASS_NAME, "shopping_cart_link")
CONTADOR_CARRITO = (By.CLASS_NAME, "shopping_cart_badge")
# XPath de la Clase 7: primer botón cuyo id contiene "add-to-cart"
BOTON_AGREGAR_PRIMERO = (By.XPATH, "(//button[contains(@id,'add-to-cart')])[1]")

# Página del carrito
ITEM_CARRITO = (By.CLASS_NAME, "cart_item")


def cargar_datos():
    """Lee el archivo datos/datos_prueba.json y lo devuelve como diccionario."""
    with open(RUTA_DATOS, encoding="utf-8") as archivo:
        return json.load(archivo)


# Se leen una sola vez al importar el módulo y se reutilizan en todos los tests
DATOS = cargar_datos()
TIEMPO_ESPERA = DATOS["tiempo_espera_segundos"]


def crear_driver():
    """Configura y devuelve una instancia del WebDriver de Chrome."""
    opciones = Options()
    # Opciones recomendadas en la Clase 8 para entornos CI o sin interfaz gráfica
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")

    # Modo headless (sin ventana): se activa con la variable de entorno HEADLESS=1
    # Útil para correr en CI/CD o en una máquina sin pantalla.
    modo_headless = os.getenv("HEADLESS") == "1"
    if modo_headless:
        opciones.add_argument("--headless=new")
        opciones.add_argument("--window-size=1920,1080")

    # Service() sin ruta: Selenium 4 busca (o descarga) el chromedriver correcto.
    # Si hace falta, indicar la ruta: Service('/ruta/a/tu/chromedriver')
    servicio = Service()

    driver = webdriver.Chrome(service=servicio, options=opciones)
    if not modo_headless:
        driver.maximize_window()  # con ventana visible, la agrandamos
    return driver


def esperar_visible(driver, localizador):
    """Espera explícita: devuelve el elemento cuando está visible en pantalla."""
    return WebDriverWait(driver, TIEMPO_ESPERA).until(
        EC.visibility_of_element_located(localizador)
    )


def realizar_login(driver, usuario=None, clave=None):
    """
    Abre saucedemo.com e inicia sesión.
    Si no se pasan usuario y clave, usa los del archivo JSON (standard_user).
    """
    usuario = usuario or DATOS["usuario_valido"]["usuario"]
    clave = clave or DATOS["usuario_valido"]["clave"]

    driver.get(DATOS["url_base"])

    # Espera explícita: el formulario de login tiene que estar visible
    campo_usuario = esperar_visible(driver, CAMPO_USUARIO)
    campo_usuario.clear()
    campo_usuario.send_keys(usuario)

    campo_clave = driver.find_element(*CAMPO_CLAVE)
    campo_clave.clear()
    campo_clave.send_keys(clave)

    driver.find_element(*BOTON_LOGIN).click()

    # Espera explícita: la URL tiene que cambiar a la página de inventario
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.url_contains("/inventory.html"))


def obtener_nombre_y_precio(tarjeta_producto):
    """Recibe la tarjeta (div.inventory_item) de un producto y devuelve (nombre, precio)."""
    nombre = tarjeta_producto.find_element(*NOMBRE_PRODUCTO).text
    precio = tarjeta_producto.find_element(*PRECIO_PRODUCTO).text
    return nombre, precio


def tomar_captura(driver, nombre_test):
    """
    Guarda una captura de pantalla en reports/capturas/ y devuelve la ruta.
    El nombre del archivo incluye el test y la fecha/hora para no pisar capturas.
    """
    os.makedirs(CARPETA_CAPTURAS, exist_ok=True)
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Los tests parametrizados tienen corchetes en el nombre: se reemplazan
    nombre_limpio = nombre_test.replace("[", "_").replace("]", "")
    ruta = os.path.join(CARPETA_CAPTURAS, f"{nombre_limpio}_{marca_tiempo}.png")
    driver.save_screenshot(ruta)
    return ruta
