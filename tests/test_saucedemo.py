"""
Pre-Entrega: Automatización de Login y Navegación Básica en saucedemo.com

Casos de prueba:
    1. Login con credenciales válidas.
    2. Navegación y verificación del catálogo.
    3. Interacción con productos (carrito).

Cada test recibe su propio navegador (fixtures definidas en conftest.py),
por eso son independientes entre sí.

Ejecutar (desde la carpeta raíz del proyecto):
    pytest tests/test_saucedemo.py -v --html=reports/reporte.html --self-contained-html
"""

import logging

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.helpers import (
    BOTON_AGREGAR_PRIMERO,
    BOTON_LOGIN,
    BOTON_MENU,
    CAMPO_CLAVE,
    CAMPO_USUARIO,
    CONTADOR_CARRITO,
    DATOS,
    FILTRO_ORDEN,
    ICONO_CARRITO,
    ITEM_CARRITO,
    TARJETAS_PRODUCTO,
    TIEMPO_ESPERA,
    TITULO_SECCION,
    esperar_visible,
    obtener_nombre_y_precio,
)

logger = logging.getLogger(__name__)

# Textos esperados, leídos del archivo datos/datos_prueba.json
TITULO_PAGINA = DATOS["textos_esperados"]["titulo_pagina"]          # "Swag Labs"
TITULO_INVENTARIO = DATOS["textos_esperados"]["titulo_inventario"]  # "Products"
TITULO_CARRITO = DATOS["textos_esperados"]["titulo_carrito"]        # "Your Cart"


# ===========================================================================
# 1. AUTOMATIZACIÓN DE LOGIN
# ===========================================================================
@pytest.mark.smoke
@pytest.mark.login
def test_login_exitoso(driver):
    """Login con standard_user / secret_sauce y redirección al inventario."""
    usuario = DATOS["usuario_valido"]["usuario"]
    clave = DATOS["usuario_valido"]["clave"]

    # Paso 1: navegar a la página de login
    driver.get(DATOS["url_base"])
    logger.info("Página de login abierta: %s", driver.current_url)

    # Paso 2: ingresar credenciales (espera explícita hasta que el campo sea visible)
    campo_usuario = esperar_visible(driver, CAMPO_USUARIO)
    campo_usuario.send_keys(usuario)
    driver.find_element(*CAMPO_CLAVE).send_keys(clave)
    driver.find_element(*BOTON_LOGIN).click()
    logger.info("Credenciales enviadas con el usuario %s", usuario)

    # Paso 3: validar el login (espera explícita hasta que cambie la URL)
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.url_contains("/inventory.html"))
    assert "/inventory.html" in driver.current_url, (
        f"No se redirigió al inventario. URL actual: {driver.current_url}"
    )

    assert driver.title == TITULO_PAGINA, (
        f"Título de la pestaña incorrecto: se esperaba '{TITULO_PAGINA}' y se obtuvo '{driver.title}'"
    )

    titulo_seccion = esperar_visible(driver, TITULO_SECCION).text
    assert titulo_seccion == TITULO_INVENTARIO, (
        f"Se esperaba el título '{TITULO_INVENTARIO}' y se obtuvo '{titulo_seccion}'"
    )

    logger.info("Login exitoso: URL con /inventory.html, título '%s' y sección '%s'",
                driver.title, titulo_seccion)


# ===========================================================================
# 2. NAVEGACIÓN Y VERIFICACIÓN DEL CATÁLOGO
# ===========================================================================
@pytest.mark.catalogo
def test_titulo_inventario(driver_logueado):
    """El título de la página de inventario es el correcto."""
    driver = driver_logueado

    assert driver.title == TITULO_PAGINA, (
        f"Título de la pestaña incorrecto: '{driver.title}'"
    )

    titulo_seccion = esperar_visible(driver, TITULO_SECCION).text
    assert titulo_seccion == TITULO_INVENTARIO, (
        f"Título de la sección incorrecto: '{titulo_seccion}'"
    )

    logger.info("Título de pestaña '%s' y de sección '%s' correctos", driver.title, titulo_seccion)


@pytest.mark.catalogo
def test_productos_visibles(driver_logueado):
    """Hay al menos un producto visible y se lista el nombre y precio del primero."""
    driver = driver_logueado

    # Espera explícita a que aparezca la primera tarjeta de producto
    primera_tarjeta = esperar_visible(driver, TARJETAS_PRODUCTO)
    productos = driver.find_elements(*TARJETAS_PRODUCTO)

    assert len(productos) > 0, "No se encontraron productos en el inventario"
    assert primera_tarjeta.is_displayed(), "El primer producto no está visible"
    logger.info("Se encontraron %d productos en el inventario", len(productos))

    nombre, precio = obtener_nombre_y_precio(primera_tarjeta)
    assert nombre != "", "El primer producto no tiene nombre"
    assert precio.startswith("$"), f"El precio del primer producto no es válido: '{precio}'"

    logger.info("Primer producto -> Nombre: %s | Precio: %s", nombre, precio)


# Parametrización (Clase 4): un sub-test por cada elemento de la interfaz
ELEMENTOS_INTERFAZ = [
    ("menu_hamburguesa", BOTON_MENU),
    ("filtro_de_orden", FILTRO_ORDEN),
    ("icono_carrito", ICONO_CARRITO),
]


@pytest.mark.catalogo
@pytest.mark.parametrize(
    "nombre_elemento, localizador",
    ELEMENTOS_INTERFAZ,
    ids=[nombre for nombre, _ in ELEMENTOS_INTERFAZ],
)
def test_elementos_interfaz_presentes(driver_logueado, nombre_elemento, localizador):
    """Los elementos importantes de la interfaz (menú, filtro, carrito) están presentes."""
    elemento = esperar_visible(driver_logueado, localizador)

    assert elemento.is_displayed(), f"El elemento '{nombre_elemento}' no está visible"
    logger.info("Elemento '%s' presente y visible", nombre_elemento)


# ===========================================================================
# 3. INTERACCIÓN CON PRODUCTOS (CARRITO)
# ===========================================================================
@pytest.mark.carrito
def test_agregar_producto_incrementa_contador(driver_logueado):
    """Al agregar el primer producto, el contador del carrito pasa de vacío a 1."""
    driver = driver_logueado

    # Antes de agregar: el contador no existe (carrito vacío)
    contadores_previos = driver.find_elements(*CONTADOR_CARRITO)
    assert len(contadores_previos) == 0, "El carrito debería empezar vacío"

    # Acción: clic en "Add to cart" del primer producto
    esperar_visible(driver, BOTON_AGREGAR_PRIMERO).click()

    # Espera explícita al contador del carrito y verificación
    contador = esperar_visible(driver, CONTADOR_CARRITO)
    assert contador.text == "1", (
        f"El contador del carrito debería mostrar 1, pero muestra {contador.text}"
    )

    logger.info("Contador del carrito incrementado correctamente: %s", contador.text)


@pytest.mark.carrito
def test_producto_aparece_en_carrito(driver_logueado):
    """El primer producto agregado aparece en el carrito con su nombre y precio."""
    driver = driver_logueado

    # Guardamos los datos del primer producto antes de agregarlo
    primera_tarjeta = esperar_visible(driver, TARJETAS_PRODUCTO)
    nombre_esperado, precio_esperado = obtener_nombre_y_precio(primera_tarjeta)

    # Agregamos el producto y esperamos a que el contador lo refleje
    esperar_visible(driver, BOTON_AGREGAR_PRIMERO).click()
    esperar_visible(driver, CONTADOR_CARRITO)

    # Navegamos al carrito
    driver.find_element(*ICONO_CARRITO).click()
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.url_contains("/cart.html"))

    titulo_carrito = esperar_visible(driver, TITULO_SECCION).text
    assert titulo_carrito == TITULO_CARRITO, (
        f"Se esperaba el título '{TITULO_CARRITO}' y se obtuvo '{titulo_carrito}'"
    )

    # Verificamos el contenido del carrito
    esperar_visible(driver, ITEM_CARRITO)
    items_carrito = driver.find_elements(*ITEM_CARRITO)
    assert len(items_carrito) == 1, (
        f"El carrito debería tener 1 producto y tiene {len(items_carrito)}"
    )

    nombre_en_carrito, precio_en_carrito = obtener_nombre_y_precio(items_carrito[0])
    assert nombre_en_carrito == nombre_esperado, (
        f"Producto incorrecto en el carrito: '{nombre_en_carrito}' (se esperaba '{nombre_esperado}')"
    )
    assert precio_en_carrito == precio_esperado, (
        f"Precio incorrecto en el carrito: '{precio_en_carrito}' (se esperaba '{precio_esperado}')"
    )

    logger.info("Producto en el carrito: %s | %s", nombre_en_carrito, precio_en_carrito)
