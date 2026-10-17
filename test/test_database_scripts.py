"""
Pruebas unitarias para la capa de scripts y conexión a base de datos.
Valida la compatibilidad de los scripts SQL y las operaciones con cursores y transacciones.
"""

import sqlite3
import unittest
from pathlib import Path

from src.database.conexion import (
    DIRECTORIO_PROYECTO,
    DIRECTORIO_SQL,
    ejecutar_script_sql,
    obtener_conexion,
)
from src.model.incapacidad import calcular_pago_incapacidad


class TestDatabaseScripts(unittest.TestCase):
    """Pruebas de la estructura y ejecución de scripts SQL."""

    def setUp(self):
        # Conexión SQLite aislada en memoria para cada prueba
        self.conexion = sqlite3.connect(":memory:")

    def tearDown(self):
        self.conexion.close()

    def test_scripts_sql_existen(self):
        """Verifica que todos los archivos SQL requeridos existan en sql/."""
        scripts_esperados = [
            "crear-tipos-incapacidad.sql",
            "datos-tipos-incapacidad.sql",
            "crear-casos-incapacidad.sql",
            "datos-ejemplo-casos.sql",
            "borrar-tablas.sql",
            "README.md",
        ]
        for script in scripts_esperados:
            ruta = DIRECTORIO_SQL / script
            self.assertTrue(ruta.exists(), f"Falta el archivo: {ruta}")

    def test_creacion_y_poblado_completo_con_scripts_sql(self):
        """Ejecuta los scripts en orden y verifica la creación e inserción de datos."""
        # 1. Crear tipos
        ejecutar_script_sql(
            DIRECTORIO_SQL / "crear-tipos-incapacidad.sql",
            conexion=self.conexion,
        )
        # 2. Datos tipos
        ejecutar_script_sql(
            DIRECTORIO_SQL / "datos-tipos-incapacidad.sql",
            conexion=self.conexion,
        )
        # 3. Crear casos
        ejecutar_script_sql(
            DIRECTORIO_SQL / "crear-casos-incapacidad.sql",
            conexion=self.conexion,
        )
        # 4. Datos casos ejemplo
        ejecutar_script_sql(
            DIRECTORIO_SQL / "datos-ejemplo-casos.sql",
            conexion=self.conexion,
        )

        cursor = self.conexion.cursor()

        # Verificar tipos
        cursor.execute("SELECT clave, nombre FROM tipos_incapacidad ORDER BY id;")
        tipos = cursor.fetchall()
        self.assertEqual(len(tipos), 3)
        self.assertEqual(tipos[0][0], "enfermedad_general")
        self.assertEqual(tipos[1][0], "maternidad")
        self.assertEqual(tipos[2][0], "riesgo_laboral")

        # Verificar casos de ejemplo
        cursor.execute("SELECT count(*) FROM casos_incapacidad;")
        total_casos = cursor.fetchone()[0]
        self.assertEqual(total_casos, 3)

        cursor.close()

    def test_borrar_tablas_script(self):
        """Verifica que borrar-tablas.sql elimine las tablas existentes."""
        # Primero crear
        ejecutar_script_sql(
            DIRECTORIO_SQL / "crear-tipos-incapacidad.sql",
            conexion=self.conexion,
        )
        ejecutar_script_sql(
            DIRECTORIO_SQL / "crear-casos-incapacidad.sql",
            conexion=self.conexion,
        )

        # Luego borrar
        ejecutar_script_sql(
            DIRECTORIO_SQL / "borrar-tablas.sql",
            conexion=self.conexion,
        )

        cursor = self.conexion.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('tipos_incapacidad', 'casos_incapacidad');"
        )
        tablas_restantes = cursor.fetchall()
        self.assertEqual(len(tablas_restantes), 0)
        cursor.close()

    def test_insercion_directa_con_cursor_y_transaccion(self):
        """Prueba inserción manual con cursor, commit y verificación con SELECT."""
        # Preparar tablas
        ejecutar_script_sql(
            DIRECTORIO_SQL / "crear-tipos-incapacidad.sql",
            conexion=self.conexion,
        )
        ejecutar_script_sql(
            DIRECTORIO_SQL / "datos-tipos-incapacidad.sql",
            conexion=self.conexion,
        )
        ejecutar_script_sql(
            DIRECTORIO_SQL / "crear-casos-incapacidad.sql",
            conexion=self.conexion,
        )

        cursor = self.conexion.cursor()
        salario = 2_000_000.0
        dias = 4
        pago = calcular_pago_incapacidad(salario, dias, "enfermedad_general")

        # Insertar
        cursor.execute(
            "INSERT INTO casos_incapacidad (tipo_id, salario, dias, pago) VALUES (?, ?, ?, ?);",
            (1, salario, dias, pago),
        )
        self.conexion.commit()

        # Verificar
        cursor.execute("SELECT salario, dias, pago FROM casos_incapacidad WHERE id = 1;")
        fila = cursor.fetchone()
        self.assertIsNotNone(fila)
        self.assertEqual(fila[0], salario)
        self.assertEqual(fila[1], dias)
        self.assertAlmostEqual(fila[2], pago, places=2)

        cursor.close()

    def test_transaccion_rollback_en_error(self):
        """Verifica que rollback revierta cambios incompletos o erróneos."""
        ejecutar_script_sql(
            DIRECTORIO_SQL / "crear-tipos-incapacidad.sql",
            conexion=self.conexion,
        )
        cursor = self.conexion.cursor()

        # Inserción sin commit
        cursor.execute("INSERT INTO tipos_incapacidad (clave, nombre) VALUES ('test_clave', 'Test');")
        # Forzar rollback
        self.conexion.rollback()

        # Verificar que no quedó guardado
        cursor.execute("SELECT * FROM tipos_incapacidad WHERE clave = 'test_clave';")
        self.assertIsNone(cursor.fetchone())
        cursor.close()

    def test_obtener_conexion_fallback_sqlite(self):
        """Prueba que obtener_conexion con fallback a SQLite funcione correctamente."""
        conn = obtener_conexion(usar_sqlite_fallback=True)
        self.assertIsInstance(conn, sqlite3.Connection)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        res = cursor.fetchone()[0]
        self.assertEqual(res, 1)
        cursor.close()
        conn.close()


if __name__ == "__main__":
    unittest.main()
