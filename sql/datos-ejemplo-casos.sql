-- ============================================================
-- Proyecto: Calculadora de Incapacidades
-- Archivo: sql/datos-ejemplo-casos.sql
-- Descripción: Inserta registros de prueba con cálculos realistas:
--              1. Enfermedad general (5 días, salario 2.500.000)
--              2. Maternidad (126 días, salario 3.000.000)
--              3. Riesgo laboral (10 días, salario 1.750.905)
-- ============================================================

INSERT INTO casos_incapacidad (fecha, tipo_id, salario, dias, pago)
VALUES
    (CURRENT_TIMESTAMP, 1, 2500000.00, 5, 277778.33),
    (CURRENT_TIMESTAMP, 2, 3000000.00, 126, 12600000.00),
    (CURRENT_TIMESTAMP, 3, 1750905.00, 10, 583635.00);
