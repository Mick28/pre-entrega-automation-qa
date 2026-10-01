# Pre-Entrega · Automatización QA — saucedemo.com

Proyecto de Pre-Entrega del curso **Automatización QA (Talento Tech)**.
Autor: **Miguel A. Escurra**

## Propósito del proyecto

Automatizar los flujos básicos de navegación del sitio de práctica [saucedemo.com](https://www.saucedemo.com) con **Selenium WebDriver y Python**, aplicando lo visto hasta la Clase 8: localización de elementos, interacciones, esperas explícitas y validaciones.

Se automatizan tres casos de prueba:

| # | Caso de prueba | Tests | Qué se valida |
|---|---|---|---|
| 1 | Login | `test_login_exitoso` | Login con `standard_user` / `secret_sauce`, espera explícita, URL con `/inventory.html`, título `Swag Labs` y sección `Products`. |
| 2 | Catálogo | `test_titulo_inventario`, `test_productos_visibles`, `test_elementos_interfaz_presentes` (x3) | Título correcto, al menos un producto visible, nombre y precio del primer producto, menú, filtro y carrito presentes. |
| 3 | Carrito | `test_agregar_producto_incrementa_contador`, `test_producto_aparece_en_carrito` | El contador pasa de vacío a `1` y el producto agregado aparece en el carrito con el mismo nombre y precio. |

Cada test abre su propio navegador, así que **los tests son independientes**: si uno falla, los demás se ejecutan igual.

## Tecnologías utilizadas

- **Python 3** — lenguaje principal
- **Pytest** — estructura de testing (fixtures, markers, parametrización)
- **Selenium WebDriver 4** — automatización del navegador
- **pytest-html** — reporte HTML de resultados
- **Git y GitHub** — control de versiones

## Estructura del proyecto

```
pre-entrega-automation-qa/
├── tests/
│   ├── __init__.py
│   └── test_saucedemo.py      # casos de prueba (login, catálogo, carrito)
├── utils/
│   ├── __init__.py
│   └── helpers.py             # funciones auxiliares y localizadores
├── datos/
│   └── datos_prueba.json      # URL, credenciales y textos esperados
├── reports/
│   ├── reporte.html           # reporte HTML generado por Pytest
│   ├── capturas/              # capturas automáticas cuando un test falla
│   └── logs/                  # logs de ejecución (ejecucion.log)
├── conftest.py                # fixtures del navegador y captura en fallos
├── pytest.ini                 # markers y configuración de logs
├── requirements.txt           # dependencias
└── README.md
```

## Instalación de dependencias

Requisitos previos: **Python 3.9 o superior** y **Google Chrome** instalado.

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/Mick28/pre-entrega-automation-qa.git
   cd pre-entrega-automation-qa
   ```

2. (Recomendado) Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

**Sobre ChromeDriver:** con Selenium 4 no hace falta descargarlo a mano; Selenium Manager busca el driver que coincide con tu versión de Chrome. Si preferís usar uno propio, indicá la ruta en `utils/helpers.py` → `Service('/ruta/a/tu/chromedriver')`.

## Cómo ejecutar las pruebas

Todos los comandos se ejecutan desde la carpeta raíz del proyecto.

**Ejecutar todo y generar el reporte HTML:**

```bash
pytest tests/test_saucedemo.py -v --html=reports/reporte.html --self-contained-html
```

**Ejecutar por grupo (markers):**

```bash
pytest -v -m smoke      # solo el login
pytest -v -m catalogo   # solo el catálogo
pytest -v -m carrito    # solo el carrito
```

**Ejecutar sin abrir ventana (modo headless):**

```bash
# Linux / macOS
HEADLESS=1 pytest -v --html=reports/reporte.html --self-contained-html
# Windows (PowerShell)
$env:HEADLESS="1"; pytest -v --html=reports/reporte.html --self-contained-html
```

## Reportes y evidencias

- **Reporte HTML:** `reports/reporte.html`. Se abre con doble clic en cualquier navegador.
- **Logs de ejecución:** `reports/logs/ejecucion.log` (también se ven en la consola mientras corren los tests).
- **Capturas de pantalla:** si un test falla, se guarda automáticamente una captura en `reports/capturas/` y se adjunta al reporte HTML.

## Datos de prueba

La URL, las credenciales y los textos esperados están en `datos/datos_prueba.json`. Para cambiar un dato no hace falta tocar el código de los tests.
