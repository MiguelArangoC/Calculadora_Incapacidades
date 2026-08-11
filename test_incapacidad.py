"""
Casos de prueba para el cálculo de pago por incapacidad.

Basado en el libro 'casos_prueba_incapacidad.xlsx':
    - 3 casos Normales       (típicos, uso cotidiano)
    - 3 casos Extraordinarios (válidos pero en los límites: salario mínimo,
                                incapacidad prolongada, valores decimales)
    - 4 casos de Error        (datos inválidos que deben ser rechazados)

Ejecutar con:
    - python -m unittest test_incapacidad.py -v
"""

import unittest
from incapacidad import calcular_pago_incapacidad


# ---------------------------------------------------------------------------
# CASOS NORMALES (1-3)
# ---------------------------------------------------------------------------

class TestCasosNormales(unittest.TestCase):

    def test_caso_1_incapacidad_estandar_5_dias(self):
        """Empleado con salario e incapacidad estándar (5 días). Caso base de referencia."""
        pago = calcular_pago_incapacidad(salario_mensual=5300000, dias_incapacidad=5)
        self.assertAlmostEqual(pago, 588918.3333333333, places=5)

    def test_caso_2_salario_medio_10_dias(self):
        """Salario medio con incapacidad de 10 días. Verifica proporcionalidad al aumentar los días."""
        pago = calcular_pago_incapacidad(salario_mensual=2500000, dias_incapacidad=10)
        self.assertAlmostEqual(pago, 555583.3333333333, places=5)

    def test_caso_3_salario_minimo_incapacidad_corta_3_dias(self):
        """Salario mínimo con incapacidad corta (3 días). Verifica el cálculo con pocos días."""
        pago = calcular_pago_incapacidad(salario_mensual=1750905, dias_incapacidad=3)
        self.assertAlmostEqual(pago, 116732.83635, places=5)


# ---------------------------------------------------------------------------
# CASOS EXTRAORDINARIOS (4-6)
# ---------------------------------------------------------------------------

class TestCasosExtraordinarios(unittest.TestCase):

    def test_caso_4_limite_inferior_1_dia(self):
        """Salario mínimo legal vigente con incapacidad mínima (1 día). Valida el límite inferior de días."""
        pago = calcular_pago_incapacidad(salario_mensual=1750905, dias_incapacidad=1)
        self.assertAlmostEqual(pago, 38910.94545, places=5)

    def test_caso_5_incapacidad_prolongada_180_dias(self):
        """Salario alto con incapacidad prolongada (180 días). Valida el límite superior de días."""
        pago = calcular_pago_incapacidad(salario_mensual=15000000, dias_incapacidad=180)
        self.assertAlmostEqual(pago, 60003000, places=5)

    def test_caso_6_salario_decimal_45_dias(self):
        """Salario con valor decimal e incapacidad de 45 días. Valida precisión numérica y redondeo."""
        pago = calcular_pago_incapacidad(salario_mensual=987654.32, dias_incapacidad=45)
        self.assertAlmostEqual(pago, 987703.7027159998, places=5)


# ---------------------------------------------------------------------------
# CASOS DE ERROR (7-10)
# ---------------------------------------------------------------------------

class TestCasosError(unittest.TestCase):

    def test_caso_7_salario_negativo(self):
        """Salario mensual negativo. Debe rechazarse por validación de datos (salario <= 0)."""
        with self.assertRaises(ValueError):
            calcular_pago_incapacidad(salario_mensual=-1000000, dias_incapacidad=5)

    def test_caso_8_salario_igual_a_cero(self):
        """Salario mensual igual a cero. Debe rechazarse por validación de datos (salario <= 0)."""
        with self.assertRaises(ValueError):
            calcular_pago_incapacidad(salario_mensual=0, dias_incapacidad=10)

    def test_caso_9_dias_incapacidad_negativos(self):
        """Número de días de incapacidad negativo. Debe rechazarse por validación de datos (días <= 0)."""
        with self.assertRaises(ValueError):
            calcular_pago_incapacidad(salario_mensual=1200000, dias_incapacidad=-3)

    def test_caso_10_salario_no_numerico(self):
        """Salario mensual no numérico (texto). Debe rechazarse por validación de tipo de dato."""
        with self.assertRaises(TypeError):
            calcular_pago_incapacidad(salario_mensual="N/A", dias_incapacidad=5)

if __name__ == "__main__":
    unittest.main()
