"""
Script para insertar un caso de incapacidad en la base de datos.
Referencia: insertar-usuario.py (https://github.com/ProfeBill/database-01)

Este script demuestra:
1. Cómo calcular el valor a pagar usando la lógica de negocio del modelo.
2. Cómo insertar un registro (DML - INSERT INTO) usando un cursor y parámetros seguros.
3. El uso de connection.commit() para confirmar la transacción.
4. Cómo verificar la persistencia del registro mediante una consulta SELECT inmediata.
5. El manejo de excepciones con connection.rollback() en caso de fallo.
"""

import sys
import sqlite3
from datetime import datetime

from src.database.conexion import (
    ErrorConexionBD,
    descripcion_conexion,
    obtener_conexion,
)
from src.model.incapacidad import calcular_pago_incapacidad


def main() -> None:
    print("=" * 60)
    print("  INSERTAR CASO DE INCAPACIDAD")
    print("=" * 60)
    print(f"Base de datos activa: {descripcion_conexion()}\n")

    # Datos del caso a calcular e insertar
    salario_mensual = 2_500_000.0
    dias_incapacidad = 5
    clave_tipo = "enfermedad_general"

    # Cálculo del pago según la legislación laboral (66.67% para enfermedad general)
    pago_calculado = calcular_pago_incapacidad(
        salario_mensual=salario_mensual,
        dias_incapacidad=dias_incapacidad,
        tipo_incapacidad=clave_tipo,
    )

    print("Datos a registrar:")
    print(f"  - Salario mensual: ${salario_mensual:,.2f} COP")
    print(f"  - Dias de incapacidad: {dias_incapacidad}")
    print(f"  - Tipo de incapacidad: {clave_tipo}")
    print(f"  - Pago calculado: ${pago_calculado:,.2f} COP\n")

    conexion = None
    try:
        # 1. Conectar a la base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # 2. Obtener el ID del tipo de incapacidad en el catálogo
        cursor.execute(
            "SELECT id, nombre FROM tipos_incapacidad WHERE clave = %s"
            if not isinstance(conexion, sqlite3.Connection)
            else "SELECT id, nombre FROM tipos_incapacidad WHERE clave = ?",
            (clave_tipo,),
        )
        tipo_fila = cursor.fetchone()
        if not tipo_fila:
            raise ValueError(
                f"El tipo '{clave_tipo}' no se encuentra en la base de datos. "
                "Asegúrese de ejecutar primero 'python crear_tablas.py'."
            )
        tipo_id, tipo_nombre = tipo_fila[0], tipo_fila[1]

        # 3. Insertar el caso (DML)
        # Usamos parámetros seguros (%s o ?) para evitar inyección SQL
        fecha_actual = datetime.now()
        param_placeholder = "%s" if not isinstance(conexion, sqlite3.Connection) else "?"

        consulta_insert = f"""
        INSERT INTO casos_incapacidad (fecha, tipo_id, salario, dias, pago)
        VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder})
        """

        cursor.execute(
            consulta_insert,
            (fecha_actual, tipo_id, salario_mensual, dias_incapacidad, pago_calculado),
        )

        # 4. Las instrucciones DML necesitan commit() para hacer los cambios persistentes
        conexion.commit()

        # 5. Obtener el ID del registro recién insertado para verificarlo
        if isinstance(conexion, sqlite3.Connection):
            cursor.execute("SELECT last_insert_rowid();")
            nuevo_id = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT LASTVAL();")
            nuevo_id = cursor.fetchone()[0]

        # 6. Verificar que haya quedado creado realizando un SELECT
        cursor.execute(
            f"SELECT c.id, c.fecha, t.nombre, c.salario, c.dias, c.pago "
            f"FROM casos_incapacidad c "
            f"JOIN tipos_incapacidad t ON c.tipo_id = t.id "
            f"WHERE c.id = {param_placeholder}",
            (nuevo_id,),
        )
        resultado = cursor.fetchone()

        print("[OK] Resultado de la consulta de verificacion:")
        print(f"  Registro recuperado: {resultado}")

        if resultado and resultado[0] == nuevo_id:
            print("\n-> Guardado OK: El caso quedo registrado exitosamente.")
        else:
            print("\n-> Error al guardar: No se encontro el registro insertado.")

        cursor.close()

    except ErrorConexionBD as err:
        print(f"\n[ERROR] Error de conexion: {err}")
        sys.exit(1)
    except Exception as err:
        print("\n[ERROR] Ocurrio un error al guardar en la base de datos:")
        print(f"  Detalle: {err}")
        if conexion:
            print("-> Deshaciendo transaccion con connection.rollback()...")
            conexion.rollback()
        sys.exit(1)
    finally:
        if conexion:
            conexion.close()
            print("[OK] Conexion cerrada.")


if __name__ == "__main__":
    main()
