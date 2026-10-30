"""
Configuración y registro de rutas/URLs para la aplicación web.

Unifica y registra los blueprints definidos en el controlador
en la aplicación Flask de la Vista.
"""

from flask import Flask
from src.controller.blueprints import casos_bp, incapacidad_bp

BLUEPRINTS = [
    incapacidad_bp,
    casos_bp,
]


def registrar_urls(app: Flask) -> None:
    """Registra todos los blueprints/URLs en la aplicación Flask."""
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

