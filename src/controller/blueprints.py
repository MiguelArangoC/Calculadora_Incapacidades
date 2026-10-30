"""
Blueprints de Flask para la Calculadora de Incapacidades.

Organiza las rutas en dos blueprints según su responsabilidad:

    incapacidad_bp  ->  GET  /
                        POST /incapacidad/calcular

    casos_bp        ->  GET  /casos
                        GET  /buscar

Cada función de vista (route handler) actúa como Controller:
recibe la request, delega la lógica al IncapacidadController y
retorna la respuesta al usuario a través de los templates (Vista).

El IncapacidadController se obtiene desde la configuración de la
aplicación Flask (`current_app.config['CONTROLLER']`), lo que permite
inyectar distintos controladores en pruebas sin modificar este módulo.
"""

from flask import Blueprint, current_app, render_template, request

from src.controller.incapacidad_controller import (
    BaseDeDatosError,
    BusquedaInvalida,
)
from src.model.incapacidad import IncapacidadError


# ============================================================
# BLUEPRINT: Formulario y Cálculo de Incapacidad
# ============================================================

incapacidad_bp = Blueprint("incapacidad", __name__)


def _obtener_controlador():
    """Obtiene el controlador registrado en la configuración de la app."""
    return current_app.config["CONTROLLER"]


def _nombre_tipo(clave: str) -> str:
    """Convierte 'enfermedad_general' a 'Enfermedad General'."""
    return clave.replace("_", " ").title()


@incapacidad_bp.route("/")
def incapacidad_form():
    """GET / — Muestra el formulario de liquidación de incapacidad."""
    return render_template("incapacidad.html")


@incapacidad_bp.route("/incapacidad/calcular", methods=["POST"])
def incapacidad_calcular():
    """
    POST /incapacidad/calcular — Calcula el pago de la incapacidad.

    Recibe los datos del formulario, delega el cálculo al Controller y
    opcionalmente guarda el caso en la base de datos.
    """
    salario_raw = request.form.get("salario", "").strip()
    dias_raw = request.form.get("dias", "").strip()
    tipo = request.form.get("tipo", "enfermedad_general").strip()
    guardar = request.form.get("guardar")

    caso_guardado = None

    try:
        # Conversión de los datos del formulario
        salario = float(salario_raw)
        dias = float(dias_raw)

        # El Controller realiza el cálculo; la Vista no llama al Modelo.
        controlador = _obtener_controlador()
        resultado = controlador.calcular_caso(
            salario=salario,
            dias=dias,
            tipo_incapacidad=tipo,
        )

        pago = resultado["pago"]
        porcentaje = resultado["porcentaje"]
        tipo_nombre = _nombre_tipo(tipo)

        if guardar:
            try:
                caso_guardado = controlador.insertar_caso(
                    salario=salario,
                    dias=dias,
                    tipo_incapacidad=tipo,
                )
            except BaseDeDatosError:
                caso_guardado = None

    except (TypeError, ValueError) as error:
        mensaje_error = (
            f"Error: salario y días deben ser números válidos. ({error})"
        )
        return render_template(
            "incapacidad.html",
            error=mensaje_error,
            salario=salario_raw,
            dias=dias_raw,
            tipo=tipo,
        ), 400

    except IncapacidadError as error:
        return render_template(
            "incapacidad.html",
            error=str(error),
            salario=salario_raw,
            dias=dias_raw,
            tipo=tipo,
        ), 400

    return render_template(
        "resultado_incapacidad.html",
        salario=salario,
        dias=dias,
        tipo=tipo,
        tipo_nombre=tipo_nombre,
        porcentaje=porcentaje,
        pago=pago,
        caso_guardado=caso_guardado,
    )


# ============================================================
# BLUEPRINT: Historial y Búsqueda de Casos
# ============================================================

casos_bp = Blueprint("casos", __name__)


@casos_bp.route("/casos")
def lista_casos():
    """GET /casos — Muestra el historial completo de casos registrados."""
    casos = []
    error = None
    try:
        controlador = _obtener_controlador()
        casos = controlador.listar_casos()
    except BaseDeDatosError as err:
        error = f"No se pudo consultar la base de datos: {err}"

    return render_template("casos.html", casos=casos, error=error)


@casos_bp.route("/buscar")
def buscar():
    """
    GET /buscar — Muestra el formulario de búsqueda.

    Si se recibe el parámetro 'query', retorna los casos coincidentes.
    """
    query = request.args.get("query")
    resultados = None
    error = None

    if query is not None:
        query = query.strip()
        if not query:
            error = "Por favor ingrese un texto o número para buscar."
        else:
            try:
                controlador = _obtener_controlador()
                resultados = controlador.buscar_casos(query)
            except BusquedaInvalida:
                error = "El término de búsqueda ingresado no es válido."
            except BaseDeDatosError as err:
                error = f"Error al consultar la base de datos: {err}"

    return render_template(
        "buscar.html",
        query=query,
        resultados=resultados,
        error=error,
    )

