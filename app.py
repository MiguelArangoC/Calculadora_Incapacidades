"""
Punto de entrada WSGI para despliegue en producción (Render, Gunicorn).

Delega la instancia de Flask a la vista web en src/view/web/app.py
manteniendo la arquitectura MVC.
"""

from src.view.web.app import app

if __name__ == "__main__":
    app.run()

