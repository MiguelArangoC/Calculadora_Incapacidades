"""
Pruebas de integración de la interfaz web Flask (MVC).

Verifica que las rutas y vistas web procesen correctamente los formularios,
deleguen al controlador y retornen los templates con los datos esperados.
"""

import unittest
from unittest.mock import MagicMock

from src.controller.incapacidad_controller import IncapacidadController
from src.view.web.app import create_app


class TestWebViews(unittest.TestCase):
    """Pruebas para las vistas web y blueprints de Flask."""

    def setUp(self):
        self.mock_controller = MagicMock(spec=IncapacidadController)
        self.app = create_app(controller=self.mock_controller)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_get_formulario_principal(self):
        """GET / carga el formulario de cálculo con status 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Calculadora de Incapacidades", response.data)

    def test_post_calcular_exitoso(self):
        """POST /incapacidad/calcular delega el cálculo al controlador y muestra el resultado."""
        self.mock_controller.calcular_caso.return_value = {
            "salario": 2500000.0,
            "dias": 5.0,
            "tipo_incapacidad": "enfermedad_general",
            "porcentaje": 0.6667,
            "pago": 277791.67,
        }

        response = self.client.post(
            "/incapacidad/calcular",
            data={
                "salario": "2500000",
                "dias": "5",
                "tipo": "enfermedad_general",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resultado de la Liquidaci", response.data)

    def test_post_calcular_invalido_retorna_400(self):
        """POST con datos no numéricos retorna código 400."""
        response = self.client.post(
            "/incapacidad/calcular",
            data={
                "salario": "invalido",
                "dias": "cinco",
                "tipo": "enfermedad_general",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Error", response.data)

    def test_get_casos_historial(self):
        """GET /casos consulta los casos mediante el controlador."""
        self.mock_controller.listar_casos.return_value = [
            {
                "id": 1,
                "fecha": "2026-11-04 10:00:00",
                "tipo_incapacidad": "enfermedad_general",
                "tipo_nombre": "Enfermedad General",
                "salario": 2000000.0,
                "dias": 4,
                "pago": 177786.67,
            }
        ]
        response = self.client.get("/casos")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enfermedad General", response.data)

    def test_get_buscar_casos(self):
        """GET /buscar con query retorna los casos encontrados."""
        self.mock_controller.buscar_casos.return_value = [
            {
                "id": 2,
                "fecha": "2026-11-04 10:00:00",
                "tipo_incapacidad": "maternidad",
                "tipo_nombre": "Maternidad",
                "salario": 3000000.0,
                "dias": 10,
                "pago": 1000000.0,
            }
        ]
        response = self.client.get("/buscar?query=Maternidad")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Maternidad", response.data)

    def test_get_formulario_contiene_seccion_primera_vez(self):
        """GET / contiene la sección y enlace de 'Uso por primera vez'."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Uso por primera vez".encode("utf-8"), response.data)
        self.assertIn("haga click aqui para crear las tablas".encode("utf-8"), response.data)
        self.assertIn(b"/crear-tablas", response.data)

    def test_crear_tablas_exitoso(self):
        """GET /crear-tablas invoca crear_tablas en el controlador y muestra mensaje de éxito."""
        response = self.client.get("/crear-tablas")
        self.assertEqual(response.status_code, 200)
        self.mock_controller.crear_tablas.assert_called_once()
        self.assertIn("Tablas creadas exitosamente".encode("utf-8"), response.data)

    def test_crear_tablas_error(self):
        """GET /crear-tablas muestra alerta cuando la BD falla."""
        from src.controller.incapacidad_controller import BaseDeDatosError
        self.mock_controller.crear_tablas.side_effect = BaseDeDatosError("crear las tablas", "Fallo de conexión")
        response = self.client.get("/crear-tablas")
        self.assertEqual(response.status_code, 200)
        self.assertIn("No se pudieron crear las tablas".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()

