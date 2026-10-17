-- ============================================================
-- Proyecto: Calculadora de Incapacidades
-- Archivo: sql/crear-tipos-incapacidad.sql
-- Descripción: Crea la tabla de catálogo de tipos de incapacidad
--              laboral reconocidos en Colombia.
-- ============================================================

CREATE TABLE IF NOT EXISTS tipos_incapacidad (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL
);
