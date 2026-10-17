"""
Script de prueba de conexión a la base de datos.
Referencia: hellodb.py (https://github.com/ProfeBill/database-01)

Este script demuestra:
1. Cómo conectarse a la base de datos (PostgreSQL o SQLite según secret_config.py).
2. Cómo crear un cursor para ejecutar sentencias SQL.
3. Cómo ejecutar consultas (SELECT) y recuperar resultados con fetchall() o fetchone().
4. Cómo cerrar los recursos de forma segura.
"""

import sys
from src.database.conexion import (
    ErrorConexionBD,
    descripcion_conexion,
    obtener_conexion,
)


def main() -> None:
    print("=" * 60)
    print("  PRUEBA DE CONEXION A LA BASE DE DATOS")
    print("=" * 60)
    print(f"Configuracion activa: {descripcion_conexion()}\n")

    conexion = None
    try:
        # 1. Obtener la conexión a la base de datos
        conexion = obtener_conexion()
        print("[OK] Conexion establecida exitosamente.")

        # 2. Todas las instrucciones se ejecutan a traves de un cursor
        cursor = conexion.cursor()

        # 3. Ejecutar una consulta de verificacion basica
        cursor.execute("SELECT 1;")
        resultado = cursor.fetchone()
        print(f"[OK] Consulta de verificacion basica exitosa: {resultado}")

        # 4. Consultar si existe el catalogo de tipos de incapacidad
        try:
            cursor.execute("SELECT id, clave, nombre FROM tipos_incapacidad ORDER BY id;")
            tipos = cursor.fetchall()
            print(f"\n[OK] Tipos de incapacidad encontrados ({len(tipos)} registros):")
            for tipo in tipos:
                print(f"   [ID: {tipo[0]}] {tipo[1]} -> {tipo[2]}")
        except Exception:
            print("\n[INFO] La tabla 'tipos_incapacidad' aun no existe en esta base de datos.")
            print("  Puede crearla ejecutando: python crear_tablas.py")
            conexion.rollback()

        # 5. Cerrar el cursor
        cursor.close()

    except ErrorConexionBD as err:
        print(f"\n[ERROR] Error al conectar con la base de datos:")
        print(f"  {err}")
        print("\nConsejo:")
        print("  1. Verifique que el servicio de PostgreSQL este activo.")
        print("  2. Si usa Neon o Render, verifique las credenciales en 'secret_config.py'.")
        print("  3. Si desea probar sin servidor, elimine o renombre 'secret_config.py'")
        print("     para que el sistema use automaticamente SQLite local.")
        sys.exit(1)
    except Exception as err:
        print(f"\n[ERROR] Ocurrio un error inesperado: {err}")
        sys.exit(1)
    finally:
        # Siempre cerrar la conexión al finalizar
        if conexion:
            conexion.close()
            print("\n[OK] Conexion cerrada correctamente.")


if __name__ == "__main__":
    main()
