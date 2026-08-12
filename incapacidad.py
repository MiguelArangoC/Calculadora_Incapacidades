"""
Módulo de cálculo de pago por incapacidad laboral en Colombia.

Fórmula:
valor_dia = salario_mensual / 30
pago = valor_dia * porcentaje_reconocimiento * dias_incapacidad

El porcentaje de reconocimiento depende del tipo de incapacidad:
- enfermedad_general: 66.67% (Decreto 3135 de 1968 / Ley 776 de 2002)
- maternidad:         100%   (Art. 236 CST, modificado por la Ley 2114 de 2021)
- riesgo_laboral:     100%   desde el primer día (Ley 776 de 2002, a cargo de la ARL)
"""

DIAS_MES = 30

# Porcentaje de reconocimiento económico según el tipo de incapacidad.
# Para agregar un nuevo tipo, basta con añadir una llave a este diccionario.
TIPOS_INCAPACIDAD = {
    "enfermedad_general": 0.6667,  # 66.67%
    "maternidad": 1.0,             # 100%
    "riesgo_laboral": 1.0,         # 100%
}


class SalarioInvalido(Exception):
    """Se dispara cuando el salario mensual es cero o negativo."""


class DiasIncapacidadInvalidos(Exception):
    """Se dispara cuando los días de incapacidad son cero o negativos."""


class TipoIncapacidadInvalido(Exception):
    """Se dispara cuando el tipo de incapacidad no existe en TIPOS_INCAPACIDAD."""


def calcular_pago_incapacidad(salario_mensual, dias_incapacidad,
                               tipo_incapacidad="enfermedad_general"):
    """
    Calcula el pago por incapacidad laboral.

    Args:
        salario_mensual (int | float): Salario mensual del empleado. Debe ser > 0.
        dias_incapacidad (int | float): Número de días de incapacidad. Debe ser > 0.
        tipo_incapacidad (str): Llave de TIPOS_INCAPACIDAD que determina el
            porcentaje de reconocimiento (por defecto "enfermedad_general").

    Returns:
        float: Valor a pagar por incapacidad.

    Raises:
        TipoIncapacidadInvalido: Si el tipo de incapacidad no existe.
        SalarioInvalido: Si el salario es negativo o cero.
        DiasIncapacidadInvalidos: Si los días de incapacidad son negativos o cero.
        TypeError: Si el salario o los días no son valores numéricos.
    """
    try:
        porcentaje = TIPOS_INCAPACIDAD[tipo_incapacidad]
    except KeyError:
        tipos_validos = ", ".join(TIPOS_INCAPACIDAD)
        raise TipoIncapacidadInvalido(
            f"Error: '{tipo_incapacidad}' no es un tipo de incapacidad válido. "
            f"Use uno de: {tipos_validos}"
        )

    try:
        if salario_mensual <= 0:
            raise SalarioInvalido("Error: el salario no puede ser negativo o cero")
        if dias_incapacidad <= 0:
            raise DiasIncapacidadInvalidos("Error: los días de incapacidad no pueden ser negativos o cero")
    except TypeError:
        raise TypeError("Error: el salario y los días de incapacidad deben ser valores numéricos")

    valor_dia = salario_mensual / DIAS_MES
    pago = valor_dia * porcentaje * dias_incapacidad
    return pago


