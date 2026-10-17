-- ============================================================
-- Proyecto: Calculadora de Incapacidades
-- Archivo: sql/borrar-tablas.sql
-- Descripción: Elimina las tablas en orden inverso de dependencia
--              para no violar restricciones de clave foránea.
-- ============================================================

DROP TABLE IF EXISTS casos_incapacidad;
DROP TABLE IF EXISTS tipos_incapacidad;
