"""
Conexión con la base de datos PostgreSQL mediante Psycopg2.

Lee la configuración en el siguiente orden de prioridad:
1. Módulo ``secret_config.py`` (entorno local).
2. Variable de entorno ``DATABASE_URL`` (estándar de Render, Neon, Heroku).
3. Variables de entorno individuales (``DB_HOST``, ``DB_USER``, etc.).

Ofrece:
- ``obtener_conexion()``: Retorna una conexión directa (psycopg2) para
  ejecutar sentencias SQL mediante cursores y gestionar transacciones
  (commit/rollback).
- ``ejecutar_script_sql()``: Ejecuta un archivo .sql en PostgreSQL.
- ``descripcion_conexion()``: Resumen seguro de la conexión activa.
"""

from pathlib import Path
from types import ModuleType
from typing import Any
import os

try:
    import psycopg2
except ImportError:
    psycopg2 = None


DIRECTORIO_PROYECTO = Path(__file__).resolve().parents[2]
DIRECTORIO_SQL = DIRECTORIO_PROYECTO / "sql"

CAMPOS_OBLIGATORIOS = ("DB_NAME",)


class ConfiguracionBDInvalida(Exception):
    """Indica que secret_config.py está incompleto o es inválido."""


class ErrorConexionBD(Exception):
    """Indica que no fue posible establecer conexión con el servidor PostgreSQL."""


def _cargar_configuracion() -> ModuleType | None:
    """Importa secret_config.py; retorna None si no existe."""
    try:
        import secret_config
        return secret_config
    except ModuleNotFoundError as error:
        if error.name == "secret_config":
            return None
        raise


def descripcion_conexion(configuracion: ModuleType | None = None) -> str:
    """Describe la conexión activa a PostgreSQL sin mostrar la contraseña."""
    if configuracion is None:
        configuracion = _cargar_configuracion()

    if configuracion is None:
        url_env = os.environ.get("DATABASE_URL")
        if url_env:
            if "@" in url_env:
                host_info = url_env.split("@")[-1]
                return f"postgresql://***@{host_info}"
            return "postgresql://*** (DATABASE_URL)"

        nombre_bd = os.environ.get("DB_NAME") or os.environ.get("PGDATABASE")
        if nombre_bd:
            host = os.environ.get("DB_HOST") or os.environ.get("PGHOST") or "localhost"
            puerto = os.environ.get("DB_PORT") or os.environ.get("PGPORT") or 5432
            usuario = os.environ.get("DB_USER") or os.environ.get("PGUSER") or "postgres"
            return f"postgresql://{usuario}:***@{host}:{puerto}/{nombre_bd}"

        return "PostgreSQL (sin configuración: configure DATABASE_URL o secret_config.py)"

    usuario = getattr(configuracion, "DB_USER", "postgres") or "postgres"
    host = getattr(configuracion, "DB_HOST", "localhost") or "localhost"
    puerto = getattr(configuracion, "DB_PORT", 5432) or 5432
    nombre_bd = getattr(configuracion, "DB_NAME", "")

    return f"postgresql://{usuario}:***@{host}:{puerto}/{nombre_bd}"


def obtener_conexion(configuracion: ModuleType | None = None) -> Any:
    """
    Retorna una conexión directa DB-API (psycopg2) a la base de datos PostgreSQL.

    Prioridad de lectura:
    1. Archivo local `secret_config.py`
    2. Variable de entorno `DATABASE_URL` (Render / Cloud)
    3. Variables de entorno individuales (`DB_NAME`, `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`)
    """
    if psycopg2 is None:
        raise ErrorConexionBD(
            "El driver 'psycopg2' no está instalado. "
            "Ejecute: pip install psycopg2-binary"
        )

    if configuracion is None:
        configuracion = _cargar_configuracion()

    # 1. Si no existe secret_config.py, consultar variables de entorno
    if configuracion is None:
        # A. Variable DATABASE_URL
        url_env = os.environ.get("DATABASE_URL")
        if url_env:
            if url_env.startswith("postgres://"):
                url_env = "postgresql://" + url_env[len("postgres://"):]
            try:
                return psycopg2.connect(url_env, connect_timeout=10)
            except Exception as error:
                raise ErrorConexionBD(
                    f"No se pudo conectar al servidor PostgreSQL mediante DATABASE_URL. Detalle: {error}"
                ) from error

        # B. Variables individuales
        nombre_bd = os.environ.get("DB_NAME") or os.environ.get("PGDATABASE")
        if nombre_bd:
            host = os.environ.get("DB_HOST") or os.environ.get("PGHOST") or "localhost"
            puerto = os.environ.get("DB_PORT") or os.environ.get("PGPORT") or 5432
            usuario = os.environ.get("DB_USER") or os.environ.get("PGUSER")
            clave = os.environ.get("DB_PASSWORD") or os.environ.get("PGPASSWORD")
            try:
                return psycopg2.connect(
                    database=nombre_bd,
                    user=usuario,
                    password=clave,
                    host=host,
                    port=puerto,
                    connect_timeout=10,
                )
            except Exception as error:
                raise ErrorConexionBD(
                    f"No se pudo conectar al servidor PostgreSQL con variables de entorno. Detalle: {error}"
                ) from error

        raise ErrorConexionBD(
            "No se encontró 'secret_config.py' ni la variable de entorno 'DATABASE_URL'. "
            "En Render, configure la variable de entorno 'DATABASE_URL' en el Dashboard de su Web Service, "
            "o agregue 'secret_config.py' como un Secret File."
        )

    faltantes = [
        campo
        for campo in CAMPOS_OBLIGATORIOS
        if not getattr(configuracion, campo, None)
    ]
    if faltantes:
        raise ConfiguracionBDInvalida(
            f"Error: secret_config.py no define: {', '.join(faltantes)}. Revise secret_config_sample.py."
        )

    host = getattr(configuracion, "DB_HOST", "localhost")
    puerto = getattr(configuracion, "DB_PORT", 5432)
    nombre_bd = configuracion.DB_NAME
    usuario = getattr(configuracion, "DB_USER", None)
    clave = getattr(configuracion, "DB_PASSWORD", None)

    try:
        return psycopg2.connect(
            database=nombre_bd,
            user=usuario,
            password=clave,
            host=host,
            port=puerto,
            connect_timeout=10,
        )
    except UnicodeDecodeError:
        raise ErrorConexionBD(
            f"No se pudo conectar al servidor PostgreSQL en host='{host}', puerto={puerto}: "
            "Conexión rechazada o servidor inalcanzable. "
            "Verifique que el servicio esté iniciado y que las credenciales en 'secret_config.py' sean correctas."
        )
    except Exception as error:
        raise ErrorConexionBD(
            f"No se pudo conectar al servidor PostgreSQL en host='{host}', base='{nombre_bd}'. Detalle: {error}"
        ) from error


def ejecutar_script_sql(
    ruta_archivo: str | Path,
    conexion: Any | None = None,
) -> None:
    """
    Lee y ejecuta un archivo .sql en la base de datos PostgreSQL.
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
        with conexion.cursor() as cursor:
            cursor.execute(contenido_sql)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cerrar_al_terminar:
            conexion.close()
