"""
Aplicación Web de Calculadora de Incapacidades Laborales con Flask.
Referencia y estructura basada en: https://github.com/ProfeBill/webserver-01

Provee una interfaz web completa para:
- Formulario de liquidación de incapacidades laborales (GET /).
- Cálculo y liquidación de auxilio económico con persistencia (POST /incapacidad/calcular).
- Historial de casos registrados en base de datos (GET /casos).
- Búsqueda de casos por ID, fecha o tipo (GET /buscar).
"""

from flask import Flask, render_template, request
from sqlalchemy import create_engine

from src.controller.incapacidad_controller import (
    BaseDeDatosError,
    BusquedaInvalida,
    IncapacidadController,
)
from src.database.conexion import RUTA_SQLITE_POR_DEFECTO
from src.model.incapacidad import (
    TIPOS_INCAPACIDAD,
    IncapacidadError,
    calcular_pago_incapacidad,
    obtener_porcentaje_reconocimiento,
)

# Flask constructor: crea una variable que representa nuestra aplicación web
app = Flask(__name__)

# Instancia del controlador de negocio y base de datos
_controller = IncapacidadController()
_controlador_inicializado = False


def obtener_controlador() -> IncapacidadController:
    """
    Retorna el controlador activo. Si la conexión a la base de datos remota
    falla o no está disponible, realiza un fallback automático a SQLite local
    (incapacidades.db) para garantizar la disponibilidad del servicio.
    """
    global _controller, _controlador_inicializado
    if not _controlador_inicializado:
        try:
            with _controller.engine.connect() as conn:
                pass
            _controller.crear_tablas()
        except Exception:
            # Fallback transparente a SQLite local
            engine_sqlite = create_engine(f"sqlite:///{RUTA_SQLITE_POR_DEFECTO}")
            _controller = IncapacidadController(engine=engine_sqlite)
            _controller.crear_tablas()
        _controlador_inicializado = True
    return _controller


def _nombre_tipo(clave: str) -> str:
    """Convierte 'enfermedad_general' a 'Enfermedad General'."""
    return clave.replace("_", " ").title()


@app.route('/')
def incapacidad_form():
    """Ruta inicial: Muestra el formulario para ingresar datos de incapacidad."""
    return render_template('incapacidad.html')


@app.route('/incapacidad/calcular', methods=['POST'])
def incapacidad_calcular():
    """
    Recibe los datos del formulario por método POST, valida la información,
    calcula el pago correspondiente y opcionalmente lo guarda en la base de datos.
    """
    salario_raw = request.form.get('salario', '').strip()
    dias_raw = request.form.get('dias', '').strip()
    tipo = request.form.get('tipo', 'enfermedad_general').strip()
    guardar = request.form.get('guardar')

    caso_guardado = None

    try:
        # Validación y conversión de tipos numéricos
        salario = float(salario_raw)
        dias = float(dias_raw)

        # Cálculo según el modelo de negocio
        pago = calcular_pago_incapacidad(
            salario_mensual=salario,
            dias_incapacidad=dias,
            tipo_incapacidad=tipo,
        )

        porcentaje = obtener_porcentaje_reconocimiento(tipo)
        tipo_nombre = _nombre_tipo(tipo)

        # Si el usuario solicitó guardar el caso en la base de datos
        if guardar:
            try:
                controlador = obtener_controlador()
                caso_guardado = controlador.insertar_caso(
                    salario=salario,
                    dias=dias,
                    tipo_incapacidad=tipo,
                )
            except BaseDeDatosError:
                caso_guardado = None

    except (TypeError, ValueError) as error:
        # Errores de conversión de tipos numéricos
        mensaje_error = f"Error: salario y días deben ser números válidos. ({error})"
        return render_template(
            'incapacidad.html',
            error=mensaje_error,
            salario=salario_raw,
            dias=dias_raw,
            tipo=tipo,
        ), 400
    except IncapacidadError as error:
        # Errores de regla de negocio (valores <= 0, tipo inválido, etc.)
        return render_template(
            'incapacidad.html',
            error=str(error),
            salario=salario_raw,
            dias=dias_raw,
            tipo=tipo,
        ), 400

    return render_template(
        'resultado_incapacidad.html',
        salario=salario,
        dias=dias,
        tipo=tipo,
        tipo_nombre=tipo_nombre,
        porcentaje=porcentaje,
        pago=pago,
        caso_guardado=caso_guardado,
    )


@app.route('/casos')
def lista_casos():
    """Muestra el historial completo de casos registrados en la base de datos."""
    casos = []
    error = None
    try:
        controlador = obtener_controlador()
        casos = controlador.listar_casos()
    except BaseDeDatosError as err:
        error = f"No se pudo consultar la base de datos: {err}"

    return render_template('casos.html', casos=casos, error=error)


@app.route('/buscar')
def buscar():
    """
    Muestra el formulario de búsqueda y, si se recibe el parámetro 'query',
    lista los casos coincidentes.
    """
    query = request.args.get('query')
    resultados = None
    error = None

    if query is not None:
        query = query.strip()
        if not query:
            error = "Por favor ingrese un texto o número para buscar."
        else:
            try:
                controlador = obtener_controlador()
                resultados = controlador.buscar_casos(query)
            except BusquedaInvalida:
                error = "El término de búsqueda ingresado no es válido."
            except BaseDeDatosError as err:
                error = f"Error al consultar la base de datos: {err}"

    return render_template(
        'buscar.html',
        query=query,
        resultados=resultados,
        error=error,
    )


# Permite ejecutar la aplicación directamente en modo debug
if __name__ == '__main__':
    app.run(debug=True)