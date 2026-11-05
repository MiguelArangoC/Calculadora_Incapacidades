"""
Conexión con la base de datos PostgreSQL mediante Psycopg2.

Lee la configuración desde ``secret_config.py`` o desde la variable
de entorno ``DATABASE_URL``.

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
            return url_env.split("@")[-1] if "@" in url_env else "PostgreSQL (DATABASE_URL)"
        return "PostgreSQL (sin configuración activa: secret_config.py no encontrado)"

    usuario = getattr(configuracion, "DB_USER", "postgres") or "postgres"
    host = getattr(configuracion, "DB_HOST", "localhost") or "localhost"
    puerto = getattr(configuracion, "DB_PORT", 5432) or 5432
    nombre_bd = getattr(configuracion, "DB_NAME", "")

    return f"postgresql://{usuario}:***@{host}:{puerto}/{nombre_bd}"


def obtener_conexion(configuracion: ModuleType | None = None) -> Any:
    """
    Retorna una conexión directa DB-API (psycopg2) a la base de datos PostgreSQL.

    Args:
        configuracion: Módulo con credenciales. Si es None, carga secret_config.py
            o la variable de entorno DATABASE_URL.

    Returns:
        Conexión directa de psycopg2.

    Raises:
        ErrorConexionBD: Si no se puede establecer la conexión o falta psycopg2.
        ConfiguracionBDInvalida: Si falta algún campo obligatorio.
    """
    if psycopg2 is None:
        raise ErrorConexionBD(
            "El driver 'psycopg2' no está instalado. "
            "Ejecute: pip install psycopg2-binary"
        )

    if configuracion is None:
        configuracion = _cargar_configuracion()

    if configuracion is None:
        url_env = os.environ.get("DATABASE_URL")
        if url_env:
            try:
                return psycopg2.connect(url_env, connect_timeout=5)
            except Exception as error:
                raise ErrorConexionBD(
                    f"No se pudo conectar al servidor PostgreSQL mediante DATABASE_URL. Detalle: {error}"
                ) from error

        raise ErrorConexionBD(
            "No se encontró 'secret_config.py' ni la variable de entorno 'DATABASE_URL'. "
            "Configure las credenciales de PostgreSQL en 'secret_config.py' a partir de 'secret_config_sample.py'."
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
            connect_timeout=5,
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

    Args:
        ruta_archivo: Ruta al archivo .sql.
        conexion: Conexión psycopg2 opcional. Si es None, abre una nueva conexión.
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
