"""
Pruebas automatizadas para la interfaz web (Flask) de la Calculadora de Incapacidades.
"""

import unittest
from app import app
from src.controller.incapacidad_controller import IncapacidadController
from test.test_casos_bd import crear_engine_en_memoria


class TestWebCalculadora(unittest.TestCase):
    """Pruebas para las rutas y vistas de la aplicación Flask."""

    def setUp(self):
        """Configura el cliente de prueba de Flask y base de datos de prueba en memoria."""
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Inyectar engine en memoria en el controlador para aislar pruebas
        self.engine = crear_engine_en_memoria()
        import app as app_module
        app_module._controller = IncapacidadController(engine=self.engine)
        app_module._controlador_inicializado = True
        app_module._controller.crear_tablas()

    def tearDown(self):
        """Cierra el engine al finalizar."""
        self.engine.dispose()

    def test_ruta_inicio_retorna_200_y_formulario(self):
        """La ruta principal GET / debe retornar 200 y mostrar el formulario."""
        respuesta = self.client.get('/')
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Liquidación de Incapacidad", contenido)
        self.assertIn('name="salario"', contenido)
        self.assertIn('name="dias"', contenido)
        self.assertIn('name="tipo"', contenido)

    def test_calcular_incapacidad_enfermedad_general_exitoso(self):
        """POST /incapacidad/calcular debe calcular y retornar 200 con el resultado."""
        datos = {
            'salario': '2500000',
            'dias': '5',
            'tipo': 'enfermedad_general',
        }
        respuesta = self.client.post('/incapacidad/calcular', data=datos)
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Resultado de la Liquidación", contenido)
        self.assertIn("277,791.67", contenido)

    def test_calcular_incapacidad_maternidad_al_100_por_ciento(self):
        """POST /incapacidad/calcular para maternidad liquida al 100%."""
        datos = {
            'salario': '3000000',
            'dias': '10',
            'tipo': 'maternidad',
        }
        # 3_000_000 / 30 * 1.0 * 10 = 1_000_000
        respuesta = self.client.post('/incapacidad/calcular', data=datos)
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("1,000,000.00", contenido)
        self.assertIn("100.00%", contenido)

    def test_calcular_incapacidad_guardar_en_bd(self):
        """POST /incapacidad/calcular con guardar=1 almacena el caso."""
        datos = {
            'salario': '2000000',
            'dias': '3',
            'tipo': 'riesgo_laboral',
            'guardar': '1',
        }
        respuesta = self.client.post('/incapacidad/calcular', data=datos)
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Registro guardado en base de datos", contenido)
        self.assertIn("#1", contenido)

    def test_calcular_error_salario_no_numerico(self):
        """POST con salario alfabético retorna 400 y mensaje de error."""
        datos = {
            'salario': 'abc',
            'dias': '5',
            'tipo': 'enfermedad_general',
        }
        respuesta = self.client.post('/incapacidad/calcular', data=datos)
        self.assertEqual(respuesta.status_code, 400)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Error: salario y días deben ser números válidos", contenido)

    def test_calcular_error_salario_negativo(self):
        """POST con salario negativo retorna 400 y mensaje de error."""
        datos = {
            'salario': '-500000',
            'dias': '5',
            'tipo': 'enfermedad_general',
        }
        respuesta = self.client.post('/incapacidad/calcular', data=datos)
        self.assertEqual(respuesta.status_code, 400)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("el salario debe ser un valor positivo", contenido)

    def test_calcular_error_dias_cero_o_negativos(self):
        """POST con 0 días retorna 400 y mensaje de error."""
        datos = {
            'salario': '2000000',
            'dias': '0',
            'tipo': 'enfermedad_general',
        }
        respuesta = self.client.post('/incapacidad/calcular', data=datos)
        self.assertEqual(respuesta.status_code, 400)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("días de incapacidad deben ser un valor positivo mayor a cero", contenido)

    def test_ruta_casos_retorna_200(self):
        """GET /casos retorna 200 y el template de historial."""
        respuesta = self.client.get('/casos')
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Historial de Incapacidades Registradas", contenido)

    def test_ruta_buscar_sin_query(self):
        """GET /buscar sin parámetros muestra el formulario de búsqueda."""
        respuesta = self.client.get('/buscar')
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Búsqueda de Casos de Incapacidad", contenido)

    def test_ruta_buscar_con_query(self):
        """GET /buscar con query retorna los resultados correspondientes."""
        # Insertar un caso para buscar
        from app import _controller
        _controller.insertar_caso(salario=2500000, dias=4, tipo_incapacidad="maternidad")

        respuesta = self.client.get('/buscar?query=maternidad')
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Resultados para:", contenido)
        self.assertIn("maternidad", contenido.lower())


if __name__ == '__main__':
    unittest.main()
