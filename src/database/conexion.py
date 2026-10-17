"""
Conexión con la base de datos.

Lee la configuración desde ``secret_config.py`` (ver
``secret_config_sample.py``). Si ese archivo no existe, usa un archivo
SQLite local (``incapacidades.db``) para que el programa siga
funcionando sin configuración.

Ofrece:
- ``obtener_conexion()``: Conexión nativa DB-API (psycopg2 o sqlite3)
  para trabajar directamente con cursores, transacciones (commit/rollback)
  y scripts SQL.
- ``obtener_engine()``: Engine SQLAlchemy compartido para el ORM.
- ``ejecutar_script_sql()``: Ejecutor de archivos .sql.
- ``descripcion_conexion()``: Resumen seguro de la conexión activa.
"""

from functools import lru_cache
from pathlib import Path
import sqlite3
from types import ModuleType
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL

from src.model.incapacidad import IncapacidadError


DIRECTORIO_PROYECTO = Path(__file__).resolve().parents[2]
DIRECTORIO_SQL = DIRECTORIO_PROYECTO / "sql"
RUTA_SQLITE_POR_DEFECTO = DIRECTORIO_PROYECTO / "incapacidades.db"

CAMPOS_OBLIGATORIOS = ("DB_DRIVER", "DB_NAME")


class ConfiguracionBDInvalida(IncapacidadError):
    """Indica que secret_config.py está incompleto o es inválido."""


class ErrorConexionBD(IncapacidadError):
    """Indica que no fue posible establecer conexión con el servidor de base de datos."""


def _cargar_configuracion() -> ModuleType | None:
    """Importa secret_config.py; retorna None si no existe."""
    try:
        import secret_config
    except ModuleNotFoundError as error:
        if error.name == "secret_config":
            return None
        raise

    return secret_config


def construir_url(configuracion: ModuleType | None = None) -> URL:
    """
    Construye la URL de conexión de SQLAlchemy.

    Args:
        configuracion: Módulo con las variables DB_*. Si es None se
            intenta importar ``secret_config``.

    Raises:
        ConfiguracionBDInvalida: Si falta un campo obligatorio.
    """
    if configuracion is None:
        configuracion = _cargar_configuracion()

    if configuracion is None:
        return URL.create(
            "sqlite", database=str(RUTA_SQLITE_POR_DEFECTO)
        )

    faltantes = [
        campo
        for campo in CAMPOS_OBLIGATORIOS
        if not getattr(configuracion, campo, None)
    ]

    if faltantes:
        raise ConfiguracionBDInvalida(
            "Error: secret_config.py no define: "
            f"{', '.join(faltantes)}. Revise secret_config_sample.py."
        )

    if configuracion.DB_DRIVER.startswith("sqlite"):
        # SQLite es un archivo local: ignora usuario, host y puerto.
        database_path = configuracion.DB_NAME
        if not Path(database_path).is_absolute():
            database_path = str(DIRECTORIO_PROYECTO / database_path)
        return URL.create(
            configuracion.DB_DRIVER, database=database_path
        )

    return URL.create(
        drivername=configuracion.DB_DRIVER,
        username=getattr(configuracion, "DB_USER", None),
        password=getattr(configuracion, "DB_PASSWORD", None),
        host=getattr(configuracion, "DB_HOST", None),
        port=getattr(configuracion, "DB_PORT", None),
        database=configuracion.DB_NAME,
    )


@lru_cache(maxsize=1)
def obtener_engine() -> Engine:
    """Retorna el engine compartido de la aplicación."""
    return create_engine(construir_url())


def descripcion_conexion(configuracion: ModuleType | None = None) -> str:
    """Describe la conexión activa sin mostrar la contraseña."""
    return construir_url(configuracion).render_as_string(hide_password=True)


def obtener_conexion(
    configuracion: ModuleType | None = None,
    usar_sqlite_fallback: bool = False,
) -> Any:
    """
    Retorna una conexión directa (DB-API) a la base de datos.

    Permite interactuar directamente mediante cursores (``cursor = conn.cursor()``),
    ejecutar sentencias SQL, y gestionar transacciones con ``conn.commit()`` y
    ``conn.rollback()``, tal como se enseña en psycopg2 / PostgreSQL.

    Args:
        configuracion: Módulo con credenciales. Si es None, carga secret_config.py.
        usar_sqlite_fallback: Si es True o no hay secret_config, usa SQLite local.

    Returns:
        Conexión directa (psycopg2.connection o sqlite3.Connection).
    """
    if usar_sqlite_fallback:
        return sqlite3.connect(str(RUTA_SQLITE_POR_DEFECTO))

    if configuracion is None:
        configuracion = _cargar_configuracion()

    if configuracion is None or configuracion.DB_DRIVER.startswith("sqlite"):
        ruta_db = RUTA_SQLITE_POR_DEFECTO
        if configuracion and getattr(configuracion, "DB_NAME", None):
            ruta_db = Path(configuracion.DB_NAME)
            if not ruta_db.is_absolute():
                ruta_db = DIRECTORIO_PROYECTO / ruta_db
        return sqlite3.connect(str(ruta_db))

    if configuracion.DB_DRIVER.startswith("postgresql"):
        try:
            import psycopg2
        except ImportError as exc:
            raise ErrorConexionBD(
                "El driver 'psycopg2' no está instalado. "
                "Ejecute: pip install psycopg2-binary"
            ) from exc

        try:
            return psycopg2.connect(
                database=configuracion.DB_NAME,
                user=getattr(configuracion, "DB_USER", None),
                password=getattr(configuracion, "DB_PASSWORD", None),
                host=getattr(configuracion, "DB_HOST", "localhost"),
                port=getattr(configuracion, "DB_PORT", 5432),
                connect_timeout=5,
            )
        except UnicodeDecodeError:
            raise ErrorConexionBD(
                f"No se pudo conectar al servidor PostgreSQL en host='{getattr(configuracion, 'DB_HOST', 'localhost')}', "
                f"puerto={getattr(configuracion, 'DB_PORT', 5432)}: "
                "Conexión rechazada o servidor inalcanzable. "
                "Verifique que el servicio esté iniciado y que el host y puerto en 'secret_config.py' sean correctos."
            )
        except Exception as error:
            raise ErrorConexionBD(
                f"No se pudo conectar al servidor PostgreSQL en "
                f"host='{getattr(configuracion, 'DB_HOST', 'localhost')}', "
                f"base='{configuracion.DB_NAME}'. Detalle: {error}"
            ) from error

    # Si es otro motor no soportado directamente por DBAPI aquí, recurre a SQLite
    return sqlite3.connect(str(RUTA_SQLITE_POR_DEFECTO))


def ejecutar_script_sql(
    ruta_archivo: str | Path,
    conexion: Any | None = None,
) -> None:
    """
    Lee y ejecuta un archivo .sql en la base de datos indicada o en la activa.

    Si la conexión es SQLite, adapta la sintaxis de autoincremento para máxima
    portabilidad. Maneja la transacción realizando commit() al finalizar.

    Args:
        ruta_archivo: Ruta al archivo .sql.
        conexion: Conexión DB-API opcional. Si es None, abre una nueva conexión.
    """
    ruta = Path(ruta_archivo)
    if not ruta.is_absolute():
        ruta = DIRECTORIO_PROYECTO / ruta

    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo SQL: {ruta}")

    contenido_sql = ruta.read_text(encoding="utf-8")

    cerrar_al_terminar = False
    if conexion is None:
        conexion = obtener_conexion()
        cerrar_al_terminar = True

    try:
        es_sqlite = isinstance(conexion, sqlite3.Connection)
        if es_sqlite:
            # Adaptación para SQLite si el script usa sintaxis PostgreSQL
            sql_adaptado = contenido_sql.replace(
                "SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT"
            )
            conexion.executescript(sql_adaptado)
        else:
            with conexion.cursor() as cursor:
                cursor.execute(contenido_sql)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cerrar_al_terminar:
            conexion.close()
