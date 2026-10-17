"""
Script para crear las tablas de la Calculadora de Incapacidades.
Referencia: crear-usuarios.py (https://github.com/ProfeBill/database-01)

Este script demuestra:
1. Cómo ejecutar sentencias DDL (CREATE TABLE) y DML (INSERT inicial).
2. El uso de connection.commit() para hacer los cambios permanentes.
3. El uso de connection.rollback() para deshacer cambios si ocurre un error.
"""

import sys
from pathlib import Path

from src.database.conexion import (
    DIRECTORIO_SQL,
    ErrorConexionBD,
    descripcion_conexion,
    ejecutar_script_sql,
    obtener_conexion,
)


SCRIPTS_CREACION = [
    ("Creando tabla 'tipos_incapacidad'...", "crear-tipos-incapacidad.sql"),
    ("Poblando catalogo 'tipos_incapacidad'...", "datos-tipos-incapacidad.sql"),
    ("Creando tabla 'casos_incapacidad'...", "crear-casos-incapacidad.sql"),
]


def main() -> None:
    print("=" * 60)
    print("  CREACION DE TABLAS - CALCULADORA DE INCAPACIDADES")
    print("=" * 60)
    print(f"Base de datos destino: {descripcion_conexion()}\n")

    conexion = None
    try:
        conexion = obtener_conexion()
        print("[OK] Conexion establecida con exito.\n")

        # Ejecución secuencial de los scripts DDL y DML
        for descripcion, archivo in SCRIPTS_CREACION:
            ruta_sql = DIRECTORIO_SQL / archivo
            print(f"-> {descripcion} ({archivo})")
            ejecutar_script_sql(ruta_sql, conexion=conexion)
            print(f"  [OK] {archivo} ejecutado correctamente.")

        # Las instrucciones DDL y DML necesitan commit() para persistir
        conexion.commit()
        print("\n[OK] Cambios confirmados permanentemente con connection.commit().")

        # Verificación con un cursor
        cursor = conexion.cursor()
        cursor.execute("SELECT count(*) FROM tipos_incapacidad;")
        total_tipos = cursor.fetchone()[0]
        print(f"[OK] Verificacion: {total_tipos} tipos de incapacidad listos en el catalogo.")
        cursor.close()

        print("\n" + "=" * 60)
        print("Todas las tablas fueron creadas exitosamente!")
        print("=" * 60)

    except ErrorConexionBD as err:
        print(f"\n[ERROR] Error de conexion: {err}")
        sys.exit(1)
    except Exception as err:
        print("\n[ERROR] Ocurrio un error al crear las tablas en la base de datos:")
        print(f"  {err}")
        if conexion:
            print("-> Revirtiendo cambios pendientes con connection.rollback()...")
            conexion.rollback()
        sys.exit(1)
    finally:
        if conexion:
            conexion.close()


if __name__ == "__main__":
    main()
