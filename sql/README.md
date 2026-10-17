# Scripts SQL - Calculadora de Incapacidades

Directorio de scripts SQL para la base de datos PostgreSQL (con compatibilidad SQLite), estructurado tomando como referencia las buenas prácticas de diseño relacional y el repositorio educativo de referencia.

## Estructura de archivos

1. **`crear-tipos-incapacidad.sql` (DDL):**
   - Crea la tabla `tipos_incapacidad` con clave primaria auto-incremental (`SERIAL`), clave única (`VARCHAR(50)`) y nombre descriptivo.
2. **`datos-tipos-incapacidad.sql` (DML):**
   - Inserta los tipos base de incapacidad: `enfermedad_general`, `maternidad` y `riesgo_laboral`.
3. **`crear-casos-incapacidad.sql` (DDL):**
   - Crea la tabla `casos_incapacidad` con clave foránea a `tipos_incapacidad(id)`, marcas de tiempo (`TIMESTAMP`) y restricciones `CHECK` que impiden salarios, días o pagos negativos o en cero.
4. **`datos-ejemplo-casos.sql` (DML):**
   - Inserta cálculos de prueba realistas para verificar consultas y reportes.
5. **`borrar-tablas.sql` (DDL):**
   - Elimina las tablas en orden respetando la integridad referencial (`casos_incapacidad` primero, luego `tipos_incapacidad`).

## Orden de ejecución recomendado

```bash
# Con psql (PostgreSQL)
psql -U postgres -d incapacidades -f sql/crear-tipos-incapacidad.sql
psql -U postgres -d incapacidades -f sql/datos-tipos-incapacidad.sql
psql -U postgres -d incapacidades -f sql/crear-casos-incapacidad.sql
psql -U postgres -d incapacidades -f sql/datos-ejemplo-casos.sql
```

O directamente mediante el script Python:

```bash
python crear_tablas.py
```
