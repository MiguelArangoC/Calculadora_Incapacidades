"""
Fábrica de la aplicación web Flask (Application Factory).

Responsabilidad de esta Vista:
    - Crear la instancia de Flask con sus carpetas de templates y static.
    - Registrar los blueprints del Controller.
    - Exponer `create_app()` para pruebas y despliegue.

Las rutas y la lógica de cada endpoint viven en:
    src/controller/blueprints.py
"""

import os

from flask import Flask

from src.controller.blueprints import casos_bp, incapacidad_bp
from src.controller.incapacidad_controller import IncapacidadController


# Raíz del proyecto (tres niveles arriba de src/view/web/)
_RAIZ_PROYECTO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)


def create_app(controller: IncapacidadController | None = None) -> Flask:
    """
    Crea y configura la aplicación Flask.

    Args:
        controller: Instancia de IncapacidadController a usar. Si es None,
            se crea una nueva con fallback automático a SQLite local.
            Pasa un controller propio en las pruebas para aislarlas.

    Returns:
        Aplicación Flask lista para usar.
    """
    flask_app = Flask(
        __name__,
        template_folder=os.path.join(_RAIZ_PROYECTO, "templates"),
        static_folder=os.path.join(_RAIZ_PROYECTO, "static"),
    )

    # El Controller se guarda en la configuración de la app para que los
    # blueprints lo obtengan con current_app.config['CONTROLLER'].
    if controller is None:
        controller = IncapacidadController()
        controller.inicializar_con_fallback()

    flask_app.config["CONTROLLER"] = controller

    # Registro de los blueprints (rutas definidas en el Controller)
    flask_app.register_blueprint(incapacidad_bp)
    flask_app.register_blueprint(casos_bp)

    return flask_app


# Instancia por defecto para ejecutar directamente con `python app.py`
# o con el servidor de Flask (`flask run`).
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
