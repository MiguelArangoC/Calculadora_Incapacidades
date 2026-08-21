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

from typing import Union

DIAS_MES = 30

# Porcentaje de reconocimiento económico según el tipo de incapacidad.
# Para agregar un nuevo tipo, basta con añadir una llave a este diccionario.
TIPOS_INCAPACIDAD = {
    "enfermedad_general": 0.6667,
    "maternidad": 1.0,
    "riesgo_laboral": 1.0,
}


class IncapacidadError(Exception):
    """Clase base para las excepciones del cálculo de incapacidad."""


class SalarioInvalido(IncapacidadError):
    """Se dispara cuando el salario mensual es cero o negativo."""


class DiasIncapacidadInvalidos(IncapacidadError):
    """Se dispara cuando los días de incapacidad son cero o negativos."""


class TipoIncapacidadInvalido(IncapacidadError):
    """Se dispara cuando el tipo de incapacidad no existe en TIPOS_INCAPACIDAD."""


def _validar_numerico(valor: Union[int, float], nombre_campo: str) -> None:
    """Valida que 'valor' sea numérico (int o float)."""
    if not isinstance(valor, (int, float)):
        raise TypeError(
            f"Error: '{nombre_campo}' debe ser un valor numérico "
            f"(recibido tipo {type(valor).__name__}: {valor!r}). "
            f"Asegúrese de proveer un número."
        )


def validar_entradas(
    salario_mensual: float,
    dias_incapacidad: float,
    tipo_incapacidad: str
) -> float:
    """
    Valida las reglas de negocio para el cálculo de incapacidades en el siguiente orden:
    1. Existencia del tipo de incapacidad.
    2. Tipos de dato numéricos para salario y días.
    3. Valores estrictamente positivos (>0) para salario y días.
    
    Retorna el porcentaje de reconocimiento aplicable.
    """
    try:
        porcentaje = TIPOS_INCAPACIDAD[tipo_incapacidad]
    except KeyError:
        tipos_validos = ", ".join(TIPOS_INCAPACIDAD)
        raise TipoIncapacidadInvalido(
            f"Error: '{tipo_incapacidad}' no es un tipo de incapacidad válido. "
            f"Use uno de: {tipos_validos}"
        )

    _validar_numerico(valor=salario_mensual, nombre_campo="salario_mensual")
    _validar_numerico(valor=dias_incapacidad, nombre_campo="dias_incapacidad")

    if salario_mensual <= 0:
        raise SalarioInvalido(
            f"Error: el salario debe ser un valor positivo mayor a cero "
            f"(recibido: {salario_mensual}). Por favor asigne un salario válido."
        )
    if dias_incapacidad <= 0:
        raise DiasIncapacidadInvalidos(
            f"Error: los días de incapacidad deben ser un valor positivo mayor a cero "
            f"(recibido: {dias_incapacidad}). Debe reportar al menos 1 día de incapacidad."
        )
        
    return porcentaje


def calcular_pago_incapacidad(
    salario_mensual: float,
    dias_incapacidad: float,
    tipo_incapacidad: str = "enfermedad_general",
) -> float:
    """
    Calcula el pago por incapacidad laboral.

    Args:
        salario_mensual (float): Salario mensual del empleado. Debe ser > 0.
        dias_incapacidad (float): Número de días de incapacidad. Debe ser > 0.
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
    porcentaje = validar_entradas(
        salario_mensual=salario_mensual,
        dias_incapacidad=dias_incapacidad,
        tipo_incapacidad=tipo_incapacidad
    )

    valor_dia = salario_mensual / DIAS_MES
    pago = valor_dia * porcentaje * dias_incapacidad
    return pago


