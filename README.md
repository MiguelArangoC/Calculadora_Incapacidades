# Calculadora de Incapacidades

Aplicación académica en Python para estimar el pago correspondiente a incapacidades laborales en Colombia.

Cuenta con interfaz web (Flask), interfaz gráfica (Kivy/KivyMD), interfaz de consola, persistencia con PostgreSQL/SQLite y generación de ejecutables para Windows y Android.

> **Nota:** Los resultados son una simulación académica y no sustituyen una liquidación oficial realizada por una entidad competente.

---

## Tabla de contenido

- [Tipos de incapacidad](#tipos-de-incapacidad)
- [Proceso de cálculo](#proceso-de-cálculo)
- [Validaciones](#validaciones)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Base de datos (ORM)](#base-de-datos-orm)
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Pruebas](#pruebas)
- [Compilación](#compilación)
- [Alcance y limitaciones](#alcance-y-limitaciones)
- [Integrantes](#integrantes)
- [Licencia](#licencia)

---

## Tipos de incapacidad

| Tipo               | Porcentaje de reconocimiento |
| ------------------ | ---------------------------: |
| Enfermedad general |                       66.67% |
| Maternidad         |                         100% |
| Riesgo laboral     |                         100% |

---

## Proceso de cálculo

Una vez validados los datos:

1. Se identifica el tipo de incapacidad y su porcentaje.
2. Se calcula el valor diario: `salario_mensual / 30`.
3. Se obtiene el pago: `valor_dia × porcentaje × dias_incapacidad`.

### Ejemplo

Salario de $2.500.000, incapacidad de 5 días por enfermedad general:

```
valor_dia = 2.500.000 / 30 = 83.333,33
pago = 83.333,33 × 0.6667 × 5 = 277.778,33
```

---

## Validaciones

Antes de calcular, el programa verifica:

- Salario mayor a cero.
- Días de incapacidad mayores a cero.
- Tipo de incapacidad válido.
- Valores numéricos.
- Datos completos.

Los errores se manejan con excepciones específicas que generan mensajes claros para el usuario.

---

## Estructura del proyecto

```
Calculadora_Incapacidades/
├── app.py                           # Servidor Web Flask (ref: webserver-01)
├── main.py                          # Punto de entrada de la app gráfica
├── probar_conexion.py               # Prueba de conexión (ref: hellodb.py)
├── crear_tablas.py                  # DDL y carga inicial (ref: crear-usuarios.py)
├── insertar_caso.py                 # Inserción con commit/rollback (ref: insertar-usuario.py)
├── consultar_casos.py               # Consulta SELECT con cursores
├── requirements.txt
├── buildozer.spec                   # Configuración Android
├── secret_config_sample.py          # Plantilla de conexión a la BD
├── secret_config.py                 # Tu conexión real (NO se sube a Git)
│
├── templates/                       # Plantillas HTML con motor Jinja2 (ref: webserver-01)
│   ├── base.html                    # Plantilla base común
│   ├── incapacidad.html             # Formulario de cálculo
│   ├── resultado_incapacidad.html   # Resultados de liquidación
│   ├── casos.html                   # Listado histórico tabulado
│   └── buscar.html                  # Búsqueda de casos con tabla de resultados
│
├── static/                          # Archivos estáticos de la interfaz web
│   └── css/
│       └── style.css                # Estilos modernos y responsivos
│
├── sql/                             # Scripts SQL (DDL y DML)
│   ├── crear-tipos-incapacidad.sql  # DDL catálogo de tipos
│   ├── datos-tipos-incapacidad.sql  # DML tipos iniciales
│   ├── crear-casos-incapacidad.sql  # DDL tabla de cálculos y restricciones
│   ├── datos-ejemplo-casos.sql      # DML registros de prueba
│   ├── borrar-tablas.sql            # DDL limpieza de tablas
│   └── README.md                    # Guía de ejecución SQL
│
├── src/
│   ├── controller/
│   │   └── incapacidad_controller.py  # Operaciones de negocio y consultas ORM
│   │
│   ├── database/
│   │   └── conexion.py              # Gestión de conexiones (psycopg2 / SQLAlchemy)
│   │
│   ├── model/
│   │   ├── incapacidad.py           # Lógica de negocio (fórmulas y validaciones)
│   │   └── orm.py                   # Modelos relacionales ORM
│   │
│   └── view/
│       ├── console/
│       │   └── cli.py               # Interfaz de consola
│       └── gui/
│           └── app.py               # Interfaz gráfica (Kivy/KivyMD)
│
├── test/
│   ├── test_incapacidad.py          # Pruebas del cálculo de incapacidad
│   ├── test_casos_bd.py             # Pruebas del Controller y ORM
│   ├── test_database_scripts.py     # Pruebas de scripts SQL, cursores y transacciones
│   └── test_web.py                  # Pruebas automatizadas de la interfaz web (Flask)
│
└── .github/workflows/
    └── build-windows.yml            # CI para generar el .exe
```

---

## Base de datos (ORM)

La capa de base de datos sigue el modelo arquitectónico y las buenas prácticas del repositorio de referencia [database-01](https://github.com/ProfeBill/database-01), adaptándolo al dominio de cálculo y registro de incapacidades laborales en Colombia.

### Tablas del sistema

| Tabla               | Tipo                 | Descripción                                                          |
| ------------------- | -------------------- | -------------------------------------------------------------------- |
| `tipos_incapacidad` | Catálogo (DDL + DML) | Tipos legales (`enfermedad_general`, `maternidad`, `riesgo_laboral`) |
| `casos_incapacidad` | Transaccional (DDL)  | Registros guardados (fecha, tipo_id, salario, días, valor a pagar)   |

### Scripts SQL (`sql/`)

Se encuentran organizados en la carpeta `sql/` con sintaxis estándar PostgreSQL y compatibilidad SQLite:

- `crear-tipos-incapacidad.sql`: Crea la tabla `tipos_incapacidad`.
- `datos-tipos-incapacidad.sql`: Inserta los valores por defecto del catálogo.
- `crear-casos-incapacidad.sql`: Crea la tabla con clave foránea a `tipos_incapacidad` y restricciones `CHECK` de valores positivos.
- `datos-ejemplo-casos.sql`: Datos de prueba simulados.
- `borrar-tablas.sql`: Eliminación ordenada para reinicio de la base de datos.

### Scripts de ciclo de vida (Referencia ProfeBill/database-01)

1. **`python probar_conexion.py`** (Referencia a `hellodb.py`):
   Verifica la conectividad al servidor (PostgreSQL en Neon, Render o local), crea un cursor, ejecuta `SELECT 1;` y consulta el catálogo.
2. **`python crear_tablas.py`** (Referencia a `crear-usuarios.py`):
   Ejecuta los scripts DDL y DML, aplica `connection.commit()` para confirmar los cambios y `connection.rollback()` ante cualquier error.
3. **`python insertar_caso.py`** (Referencia a `insertar-usuario.py`):
   Calcula el pago de una incapacidad, lo inserta de manera parametrizada (evitando inyección SQL), hace commit, verifica con `SELECT` y confirma el guardado.
4. **`python consultar_casos.py`**:
   Consulta los casos registrados usando `SELECT ... JOIN` y los presenta tabulados.

### 1. Creación y configuración de la base de datos

#### A. Crear la base de datos en el servidor (PostgreSQL / MySQL)

Si utilizas un servidor PostgreSQL (local, Docker o en la nube como Render o Neon), crea la base de datos antes de ejecutar los scripts de creación de tablas:

```bash
# Con psql (PostgreSQL):
psql -U postgres -c "CREATE DATABASE incapacidades;"

# O con la utilidad createdb de PostgreSQL:
createdb -U postgres incapacidades
```

> **Nota para SQLite:** Si no deseas configurar un servidor PostgreSQL, no requieres crear ninguna base de datos previa. Si omites `secret_config.py` o configuras `DB_DRIVER = "sqlite"`, el sistema creará y usará automáticamente un archivo local `incapacidades.db`.

#### B. Configurar credenciales de conexión (`secret_config.py`)

Copia la plantilla y edítala con tus datos:

```bash
copy secret_config_sample.py secret_config.py     # Windows
# cp secret_config_sample.py secret_config.py     # Linux/macOS
```

Configura los datos de tu base de datos:

```python
DB_DRIVER = "postgresql+psycopg2"
DB_USER = "tu_usuario"
DB_PASSWORD = "tu_password"
DB_HOST = "localhost"  # O tu host en Render / Neon
DB_PORT = 5432
DB_NAME = "incapacidades"
```

### 2. Crear las tablas y probar la conexión

Una vez creada la base de datos y configurado `secret_config.py`:

```bash
python probar_conexion.py
python crear_tablas.py
python insertar_caso.py
python consultar_casos.py
```

---

## Tecnologías

- **Lenguaje:** Python 3.12
- **Servidor Web:** Flask 3.x, motor de plantillas Jinja2, HTML5 y CSS3 moderno (arquitectura [webserver-01](https://github.com/ProfeBill/webserver-01))
- **Interfaz Gráfica:** Kivy 2.3, KivyMD 2.0
- **Base de Datos y Persistencia:** PostgreSQL, SQLite local, SQLAlchemy 2.0 (ORM) y psycopg2
- **Pruebas Automatizadas:** Pytest y Unittest (cobertura unitaria y de integración)
- **Empaquetado y Compilación:** Buildozer (Android APK) y PyInstaller (ejecutable Windows)

---

## Requisitos

- Python 3.12 (Obligatorio), una versión mayor de Python no correrá la interfaz gráfica.
- Git.
- Dependencias listadas en `requirements.txt`.

---

## Instalación

```bash
git clone https://github.com/MiguelArangoC/Calculadora_Incapacidades.git
cd Calculadora_Incapacidades

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Ejecución

### Interfaz web (Flask)

Basada en el repositorio y conceptos de referencia [webserver-01](https://github.com/ProfeBill/webserver-01):

```bash
python app.py
```

O utilizando el comando de ejecución de Flask en modo Debug (con recarga automática):

```bash
python -m flask run --debug
```

Una vez en ejecución, acceda en su navegador web a: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

**Rutas y funcionalidades web:**
- **`/` (GET):** Formulario para ingresar salario mensual, días de incapacidad y seleccionar el tipo legal (`enfermedad_general`, `maternidad`, `riesgo_laboral`).
- **`/incapacidad/calcular` (POST):** Procesa los datos enviados, ejecuta el cálculo en el modelo, valida errores (con código HTTP 400), opcionalmente guarda el caso en la base de datos y muestra la tarjeta de liquidación detallada.
- **`/casos` (GET):** Consulta y presenta en una tabla con diseño moderno el historial completo de casos registrados en la base de datos (con sumatorias de días y pagos).
- **`/buscar` (GET):** Permite filtrar y buscar registros por ID, fecha o tipo de incapacidad mediante el parámetro `query`.

### Interfaz gráfica (KivyMD)

```bash
python main.py
```

La interfaz gráfica permite:

- **Calcular y guardar incapacidades (INSERT):** ingresa salario, días y selecciona el tipo de incapacidad con los botones de selección; al pulsar _"Calcular Pago"_ se liquida el valor y se guarda el caso en la base de datos.
- **Buscar y consultar casos (SELECT):** en la tarjeta _"Historial de Cálculos"_, dispone de un campo de texto para buscar por ID de caso, tipo o fecha (`AAAA-MM-DD`), botón _"Buscar"_ y botón _"Todos"_ para restaurar el listado completo.

### Interfaz de consola

```bash
python -m src.view.console.cli
```

Ofrece un menú interactivo con las siguientes opciones:

1. **Calcular y guardar incapacidad:** solicita los datos, calcula el pago y registra el caso en la base de datos.
2. **Buscar casos guardados:** permite filtrar registros por ID, fecha o tipo de incapacidad.
3. **Ver todos los casos:** lista todos los registros guardados del más reciente al más antiguo.
4. **Crear tablas:** ejecuta la creación de tablas DDL y la carga del catálogo inicial.
5. **Borrar tablas:** elimina las tablas y sus registros previa confirmación del usuario.
6. **Salir.**

---

## Pruebas

```bash
python -m pytest
```

O con `unittest`:

```bash
python -m unittest discover -s test -v
```

Las pruebas de base de datos (`test/test_casos_bd.py`) usan SQLite en memoria:
no necesitan servidor ni `secret_config.py`. El fixture `BaseDatosTestCase`
crea las tablas en `setUp` y las borra en `tearDown`. Cubren crear y borrar
tablas, insertar y buscar, cada uno con casos normales y de error.

---

## Compilación

### Windows

El workflow de GitHub Actions (`.github/workflows/build-windows.yml`) ejecuta las pruebas y genera el ejecutable con PyInstaller. El artefacto resultante se publica como `CalculadoraIncapacidades-Windows`.

Para generar el ejecutable manualmente:

```bash
python -m PyInstaller --noconfirm --clean --onedir --windowed \
    --name CalculadoraIncapacidades --paths . src/view/gui/app.py
```

### Android

La configuración se encuentra en `buildozer.spec`. Para generar el APK en un entorno compatible:

```bash
buildozer android debug
```

---

## Alcance y limitaciones

- Los porcentajes y reglas corresponden a la lógica académica del proyecto.
- No se contemplan todos los escenarios administrativos de una liquidación real.
- Los resultados no deben interpretarse como asesoría legal o laboral.

---

## Integrantes

### Desarrollo base

Lógica inicial del proyecto suministrada por el docente:

- Miguel Ángel Arango Cardona
- Juan Camilo García Castro

### Desarrollo de GUI y aplicación móvil

| Integrante              | GitHub                                             |
| ----------------------- | -------------------------------------------------- |
| Isabella Ruiz Velasquez | [@IRVMakiAkame0](https://github.com/IRVMakiAkame0) |
| Andrés Rosas            | [@andres-rosas](https://github.com/andres-rosas)   |

---

## Licencia

Proyecto desarrollado con fines académicos para la aplicación de principios de Clean Code y buenas prácticas de desarrollo de software.
