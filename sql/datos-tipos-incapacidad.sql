-- ============================================================
-- Proyecto: Calculadora de Incapacidades
-- Archivo: sql/datos-tipos-incapacidad.sql
-- Descripción: Inserta el catálogo inicial de tipos de incapacidad
--              conforme a la legislación laboral colombiana:
--              - Enfermedad General (reconoce 66.67%)
--              - Maternidad (reconoce 100%)
--              - Riesgo Laboral (reconoce 100%)
-- ============================================================

INSERT INTO tipos_incapacidad (clave, nombre)
VALUES 
    ('enfermedad_general', 'Enfermedad General'),
    ('maternidad', 'Maternidad'),
    ('riesgo_laboral', 'Riesgo Laboral')
ON CONFLICT (clave) DO NOTHING;
