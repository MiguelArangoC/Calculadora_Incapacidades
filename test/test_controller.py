"""
Pruebas unitarias para IncapacidadController con PostgreSQL (mediante Psycopg2).

Utiliza un mock de conexión para verificar la lógica del controlador,
el manejo de transacciones, las consultas SQL generadas y las excepciones,
sin requerir conectividad de red externa durante la ejecución de pruebas.
"""

from datetime import datetime
import unittest
from unittest.mock import MagicMock

from src.controller.incapacidad_controller import (
    BaseDeDatosError,
    BusquedaInvalida,
    CasoNoEncontrado,
    DiasNoEnteros,
    IncapacidadController,
)
from src.model.incapacidad import SalarioInvalido


class TestIncapacidadController(unittest.TestCase):
    """Pruebas del controlador de incapacidades."""

    def setUp(self):
        self.mock_cursor = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        self.mock_factory = MagicMock(return_value=self.mock_conn)
        self.controller = IncapacidadController(conexion_factory=self.mock_factory)

    def test_calcular_caso_sin_persistencia(self):
        """Calcula el caso correctamente sin interactuar con la base de datos."""
        res = self.controller.calcular_caso(
            salario=3_000_000,
            dias=10,
            tipo_incapacidad="maternidad",
        )
        self.assertEqual(res["salario"], 3_000_000)
        self.assertEqual(res["dias"], 10)
        self.assertEqual(res["tipo_incapacidad"], "maternidad")
        self.assertEqual(res["porcentaje"], 1.0)
        self.assertEqual(res["pago"], 1_000_000.0)
        self.mock_factory.assert_not_called()

    def test_insertar_caso_exitoso(self):
        """Inserta un caso utilizando parámetros SQL seguros y retorna el diccionario esperado."""
        self.mock_cursor.fetchone.side_effect = [
            (1, "Enfermedad General"),          # SELECT tipo_id, tipo_nombre
            (42, datetime(2026, 11, 4, 10, 0)), # RETURNING id, fecha
        ]

        caso = self.controller.insertar_caso(
            salario=2_500_000,
            dias=5,
            tipo_incapacidad="enfermedad_general",
        )

        self.assertEqual(caso["id"], 42)
        self.assertEqual(caso["tipo_incapacidad"], "enfermedad_general")
        self.assertEqual(caso["tipo_nombre"], "Enfermedad General")
        self.assertEqual(caso["dias"], 5)
        self.assertAlmostEqual(caso["pago"], 277_791.66666, places=1)
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_insertar_caso_rechaza_dias_no_enteros(self):
        """Rechaza días con decimales lanzando DiasNoEnteros."""
        with self.assertRaises(DiasNoEnteros):
            self.controller.insertar_caso(
                salario=2_000_000,
                dias=5.5,
                tipo_incapacidad="enfermedad_general",
            )
        self.mock_factory.assert_not_called()

    def test_insertar_caso_rechaza_salario_invalido(self):
        """Rechaza salario negativo mediante SalarioInvalido."""
        with self.assertRaises(SalarioInvalido):
            self.controller.insertar_caso(
                salario=-100,
                dias=5,
                tipo_incapacidad="enfermedad_general",
            )

    def test_listar_casos_retorna_lista(self):
        """Retorna la lista de casos tabulados desde PostgreSQL."""
        self.mock_cursor.fetchall.return_value = [
            (1, datetime(2026, 11, 4, 10, 0), "maternidad", "Maternidad", 3000000.0, 10, 1000000.0),
        ]

        casos = self.controller.listar_casos()
        self.assertEqual(len(casos), 1)
        self.assertEqual(casos[0]["id"], 1)
        self.assertEqual(casos[0]["tipo_nombre"], "Maternidad")
        self.assertEqual(casos[0]["pago"], 1000000.0)
        self.mock_conn.close.assert_called_once()

    def test_buscar_casos_valida_texto(self):
        """Rechaza búsquedas vacías con BusquedaInvalida."""
        with self.assertRaises(BusquedaInvalida):
            self.controller.buscar_casos("   ")

    def test_buscar_casos_exitoso(self):
        """Busca registros con ILIKE."""
        self.mock_cursor.fetchall.return_value = [
            (2, datetime(2026, 11, 4, 10, 0), "riesgo_laboral", "Riesgo Laboral", 1500000.0, 3, 150000.0),
        ]
        resultados = self.controller.buscar_casos("riesgo")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["tipo_incapacidad"], "riesgo_laboral")

    def test_buscar_caso_por_id_existente(self):
        """Recupera un caso por su clave primaria."""
        self.mock_cursor.fetchone.return_value = (
            5, datetime(2026, 11, 4, 10, 0), "enfermedad_general", "Enfermedad General", 2000000.0, 4, 177786.66
        )
        caso = self.controller.buscar_caso_por_id(5)
        self.assertEqual(caso["id"], 5)

    def test_buscar_caso_por_id_no_encontrado(self):
        """Lanza CasoNoEncontrado si la fila no existe."""
        self.mock_cursor.fetchone.return_value = None
        with self.assertRaises(CasoNoEncontrado):
            self.controller.buscar_caso_por_id(999)

    def test_falla_bd_lanza_basededatoserror(self):
        """Cualquier excepción inesperada de la BD se envuelve en BaseDeDatosError."""
        self.mock_cursor.execute.side_effect = Exception("Conexión perdida")
        with self.assertRaises(BaseDeDatosError):
            self.controller.listar_casos()


if __name__ == "__main__":
    unittest.main()

