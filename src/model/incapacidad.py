"""
Módulo de cálculo de pago por incapacidad laboral en Colombia.

Fórmula:
    valor_dia = salario_mensual / 30
    pago = valor_dia * porcentaje_reconocimiento * dias_incapacidad

El porcentaje de reconocimiento depende del tipo de incapacidad:
    - enfermedad_general: 66.67% (Decreto 3135 de 1968 / Ley 776 de 2002)
    - maternidad: 100% (Art. 236 CST, modificado por la Ley 2114 de 2021)
    - riesgo_laboral: 100% desde el primer día (Ley 776 de 2002, a cargo de la ARL)
"""

from typing import Iterable, Union

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


class ValorNoNumerico(IncapacidadError, TypeError):
    """Se dispara cuando un campo que debía ser numérico no lo es."""

    def __init__(self, nombre_campo: str, valor: object) -> None:
        self.nombre_campo = nombre_campo
        self.valor = valor
        mensaje = (
            f"Error: '{nombre_campo}' debe ser un valor numérico "
            f"(recibido: {valor}). Por favor ingrese un número."
        )
        super().__init__(mensaje)


class SalarioInvalido(IncapacidadError):
    """Se dispara cuando el salario mensual es cero o negativo."""

    def __init__(self, salario_mensual: float) -> None:
        self.salario_mensual = salario_mensual
        mensaje = (
            f"Error: el salario debe ser un valor positivo mayor a cero "
            f"(recibido: {salario_mensual}). Por favor asigne un salario válido."
        )
        super().__init__(mensaje)


class DiasIncapacidadInvalidos(IncapacidadError):
    """Se dispara cuando los días de incapacidad son cero o negativos."""

    def __init__(self, dias_incapacidad: float) -> None:
        self.dias_incapacidad = dias_incapacidad
        mensaje = (
            f"Error: los días de incapacidad deben ser un valor positivo mayor a cero "
            f"(recibido: {dias_incapacidad}). Debe reportar al menos 1 día de incapacidad."
        )
        super().__init__(mensaje)


class TipoIncapacidadInvalido(IncapacidadError):
    """Se dispara cuando el tipo de incapacidad no existe en TIPOS_INCAPACIDAD."""

    def __init__(self, tipo_incapacidad: str, tipos_validos: Iterable[str]) -> None:
        self.tipo_incapacidad = tipo_incapacidad
        mensaje = (
            f"Error: '{tipo_incapacidad}' no es un tipo de incapacidad válido. "
            f"Use uno de: {', '.join(tipos_validos)}"
        )
        super().__init__(mensaje)


def _validar_numerico(valor: Union[int, float], nombre_campo: str) -> None:
    """Valida que 'valor' sea numérico (int o float)."""
    if not isinstance(valor, (int, float)):
        raise ValorNoNumerico(nombre_campo=nombre_campo, valor=valor)


def validar_salario(salario_mensual: float) -> None:
    """
    Valida las reglas de negocio del salario mensual:
        1. Debe ser un valor numérico.
        2. Debe ser estrictamente positivo (>0).

    Raises:
        ValorNoNumerico: Si el salario no es un valor numérico.
        SalarioInvalido: Si el salario es negativo o cero.
    """
    _validar_numerico(valor=salario_mensual, nombre_campo="salario_mensual")

    if salario_mensual <= 0:
        raise SalarioInvalido(salario_mensual)


def validar_dias_incapacidad(dias_incapacidad: float) -> None:
    """
    Valida las reglas de negocio de los días de incapacidad:
        1. Deben ser un valor numérico.
        2. Deben ser estrictamente positivos (>0).

    Raises:
        ValorNoNumerico: Si los días no son un valor numérico.
        DiasIncapacidadInvalidos: Si los días de incapacidad son negativos o cero.
    """
    _validar_numerico(valor=dias_incapacidad, nombre_campo="dias_incapacidad")

    if dias_incapacidad <= 0:
        raise DiasIncapacidadInvalidos(dias_incapacidad)


def validar_entradas(salario_mensual: float, dias_incapacidad: float) -> None:
    """
    Orquesta la validación de las entradas del cálculo de incapacidad,
    delegando cada regla de negocio a su propio validador.

    Raises:
        ValorNoNumerico: Si el salario o los días no son valores numéricos.
        SalarioInvalido: Si el salario es negativo o cero.
        DiasIncapacidadInvalidos: Si los días de incapacidad son negativos o cero.
    """
    validar_salario(salario_mensual=salario_mensual)
    validar_dias_incapacidad(dias_incapacidad=dias_incapacidad)


def obtener_porcentaje_reconocimiento(tipo_incapacidad: str) -> float:
    """
    Busca el porcentaje de reconocimiento económico asociado a un tipo de incapacidad.

    Raises:
        TipoIncapacidadInvalido: Si el tipo de incapacidad no existe en TIPOS_INCAPACIDAD.

    Returns:
        float: Porcentaje de reconocimiento aplicable.
    """
    try:
        return TIPOS_INCAPACIDAD[tipo_incapacidad]
    except KeyError:
        raise TipoIncapacidadInvalido(
            tipo_incapacidad=tipo_incapacidad,
            tipos_validos=TIPOS_INCAPACIDAD,
        )


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
        ValorNoNumerico: Si el salario o los días no son valores numéricos.
    """
    porcentaje = obtener_porcentaje_reconocimiento(tipo_incapacidad=tipo_incapacidad)
    validar_entradas(salario_mensual=salario_mensual, dias_incapacidad=dias_incapacidad)

    valor_dia = salario_mensual / DIAS_MES
    pago = valor_dia * porcentaje * dias_incapacidad

    return pago
