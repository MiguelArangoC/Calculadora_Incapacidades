"""
Script para consultar y listar los casos de incapacidad guardados.
Demuestra el uso de SELECT con JOIN y cursor.fetchall().
"""

import sys
from src.database.conexion import (
    ErrorConexionBD,
    descripcion_conexion,
    obtener_conexion,
)


def main() -> None:
    print("=" * 60)
    print("  CONSULTA DE CASOS GUARDADOS EN LA BASE DE DATOS")
    print("=" * 60)
    print(f"Base de datos activa: {descripcion_conexion()}\n")

    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        consulta = """
        SELECT 
            c.id,
            c.fecha,
            t.nombre AS tipo,
            c.salario,
            c.dias,
            c.pago
        FROM casos_incapacidad c
        JOIN tipos_incapacidad t ON c.tipo_id = t.id
        ORDER BY c.id DESC;
        """

        cursor.execute(consulta)
        registros = cursor.fetchall()

        if not registros:
            print("[INFO] No hay casos registrados aun en la base de datos.")
            print("  Puede insertar uno ejecutando: python insertar_caso.py")
        else:
            print(f"Total de casos encontrados: {len(registros)}\n")
            encabezado = f"{'ID':<6} | {'FECHA':<19} | {'TIPO':<20} | {'DIAS':<6} | {'SALARIO':<15} | {'PAGO':<15}"
            print(encabezado)
            print("-" * len(encabezado))

            for fila in registros:
                id_caso, fecha, tipo_nom, salario, dias, pago = fila
                fecha_str = str(fecha)[:19]
                print(
                    f"{id_caso:<6} | {fecha_str:<19} | {tipo_nom:<20} | {dias:<6} | "
                    f"${float(salario):>13,.2f} | ${float(pago):>13,.2f}"
                )

        cursor.close()

    except ErrorConexionBD as err:
        print(f"\n[ERROR] Error de conexion: {err}")
        sys.exit(1)
    except Exception as err:
        print(f"\n[ERROR] Error al consultar los registros: {err}")
        sys.exit(1)
    finally:
        if conexion:
            conexion.close()


if __name__ == "__main__":
    main()
