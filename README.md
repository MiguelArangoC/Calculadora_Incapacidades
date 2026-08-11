# Calculadora de Incapacidades

Este proyecto contiene una calculadora sencilla para determinar el pago correspondiente a incapacidades de origen común, basada en la legislación laboral colombiana.

## Entradas (Inputs)

El programa recibe la información a través de la función `calcular_pago_incapacidad`, la cual toma los siguientes parámetros:

1. **`salario_mensual`** (`int` o `float`): El salario mensual del empleado. Debe ser un valor numérico mayor a cero.
2. **`dias_incapacidad`** (`int` o `float`): El número de días que el empleado estará incapacitado. Debe ser un valor numérico mayor a cero.
3. **`porcentaje`** (`float`, opcional): El porcentaje de reconocimiento económico. Por defecto, es `0.6667` (66.67%), correspondiente a la norma laboral para incapacidades de origen común.

### Validaciones

El programa realiza validaciones sobre los datos de entrada para garantizar que sean correctos:

- Si los valores ingresados no son numéricos (ej. texto o booleanos), arrojará un error `TypeError`.
- Si los valores ingresados son menores o iguales a cero, arrojará un error `ValueError`.

## Proceso (Process)

Una vez validados los datos de entrada, el programa realiza los siguientes cálculos matemáticos de manera interna:

1. **Cálculo del valor diario:** Divide el `salario_mensual` entre 30 (días estándar del mes laboral) para obtener cuánto gana el empleado en un día.
   > `valor_dia = salario_mensual / 30`
2. **Cálculo del pago por incapacidad:** Multiplica el valor de un día de trabajo por el porcentaje de reconocimiento (66.67%) y luego lo multiplica por el número de días de incapacidad.
   > `pago = valor_dia * porcentaje * dias_incapacidad`

## Salida (Outputs)

El programa retorna (devuelve) un valor de tipo `float` (número con decimales) que representa el monto total en dinero que el empleado debe recibir por el periodo de incapacidad reportado.

## Pruebas (Tests)

El proyecto incluye un archivo `test_incapacidad.py` que se puede ejecutar para verificar el correcto funcionamiento del programa frente a diversos casos normales, extraordinarios y de error.

```bash
python -m unittest test_incapacidad.py -v
```

## Integrantes

- Miguel Angel Arango Cardona
- Juan Camilo García Castro
