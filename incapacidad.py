"""
Módulo de cálculo de pago por incapacidad de origen común.

Fórmula:
valor_dia = salario_mensual / 30
pago = valor_dia * PORCENTAJE_RECONOCIMIENTO * dias_incapacidad

El 66.67% corresponde al porcentaje de reconocimiento económico por
incapacidad de origen común en la legislación laboral colombiana.
"""

PORCENTAJE_RECONOCIMIENTO = 0.6667  # 66.67%
DIAS_MES = 30


def calcular_pago_incapacidad(salario_mensual, dias_incapacidad,
                               porcentaje=PORCENTAJE_RECONOCIMIENTO):
    """
    Calcula el pago por incapacidad de origen común.

    Args:
        salario_mensual (int | float): Salario mensual del empleado. Debe ser > 0.
        dias_incapacidad (int | float): Número de días de incapacidad. Debe ser > 0.
        porcentaje (float): Porcentaje de reconocimiento (por defecto 66.67%).

    Returns:
        float: Valor a pagar por incapacidad.

    Raises:
        TypeError: Si el salario o los días no son numéricos.
        ValueError: Si el salario o los días son negativos o cero.
    """
    try:
        if salario_mensual <= 0:
            raise ValueError("Error: el salario no puede ser negativo o cero")
        if dias_incapacidad <= 0:
            raise ValueError("Error: los días de incapacidad no pueden ser negativos o cero")
    except TypeError:
        # Si la comparación falla es porque el dato no es numérico
        # (por ejemplo, un texto). Se relanza como TypeError con mensaje claro.
        raise TypeError("Error: el salario y los días de incapacidad deben ser valores numéricos")

    valor_dia = salario_mensual / DIAS_MES
    pago = valor_dia * porcentaje * dias_incapacidad
    return pago

