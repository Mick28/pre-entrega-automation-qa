"""
conftest.py: archivo especial de Pytest.

Todo lo que se define acá (fixtures y hooks) queda disponible
automáticamente para todos los tests del proyecto, sin importarlo.

- Fixture "driver": abre un navegador nuevo para CADA test y lo cierra al final.
  Así los tests son independientes: la falla de uno no afecta a los demás.
- Fixture "driver_logueado": igual que "driver", pero ya con la sesión iniciada.
- Hook de reporte: si un test falla, toma una captura de pantalla automática,
  la guarda en reports/capturas/ y la adjunta al reporte HTML.
"""

import logging

import pytest

from utils.helpers import crear_driver, realizar_login, tomar_captura

logger = logging.getLogger(__name__)


@pytest.fixture
def driver():
    """Prepara el navegador antes del test y lo cierra después (yield)."""
    navegador = crear_driver()
    logger.info("Navegador abierto")
    yield navegador
    # Todo lo que está después del yield se ejecuta al terminar el test,
    # haya pasado o fallado: cierre limpio, sin procesos zombis.
    navegador.quit()
    logger.info("Navegador cerrado")


@pytest.fixture
def driver_logueado(driver):
    """Reutiliza la fixture "driver" y deja la sesión iniciada con standard_user."""
    realizar_login(driver)
    logger.info("Login previo realizado: estamos en %s", driver.current_url)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest llama a esta función después de cada etapa de un test.
    Si la etapa "call" (la ejecución del test) falló, sacamos una captura.
    """
    resultado = yield
    reporte = resultado.get_result()

    if reporte.when == "call" and reporte.failed:
        navegador = item.funcargs.get("driver")
        if navegador is None:
            return

        ruta_captura = tomar_captura(navegador, item.name)
        logger.error("Test fallido: %s. Captura guardada en %s", item.name, ruta_captura)

        # Adjuntamos la captura al reporte HTML (si pytest-html está instalado)
        plugin_html = item.config.pluginmanager.getplugin("html")
        if plugin_html is not None:
            extras = getattr(reporte, "extras", [])
            extras.append(plugin_html.extras.png(navegador.get_screenshot_as_base64()))
            reporte.extras = extras
