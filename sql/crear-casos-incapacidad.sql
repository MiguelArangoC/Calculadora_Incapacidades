-- ============================================================
-- Proyecto: Calculadora de Incapacidades
-- Archivo: sql/crear-casos-incapacidad.sql
-- Descripción: Crea la tabla de casos guardados de incapacidad.
--              Contiene las restricciones de integridad relacional
--              y de verificación (CHECK) de datos válidos.
-- ============================================================

CREATE TABLE IF NOT EXISTS casos_incapacidad (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_id INTEGER NOT NULL,
    salario NUMERIC(14, 2) NOT NULL,
    dias INTEGER NOT NULL,
    pago NUMERIC(14, 2) NOT NULL,
    CONSTRAINT fk_casos_tipo FOREIGN KEY (tipo_id)
        REFERENCES tipos_incapacidad (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_salario_positivo CHECK (salario > 0),
    CONSTRAINT chk_dias_positivos CHECK (dias > 0),
    CONSTRAINT chk_pago_positivo CHECK (pago > 0)
);
