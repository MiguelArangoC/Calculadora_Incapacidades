"""
Plantilla de configuración de la base de datos PostgreSQL.

INSTRUCCIONES DE USO
--------------------
1. Copia este archivo con el nombre ``secret_config.py`` en la misma
   carpeta (la raíz del proyecto, junto a ``main.py``):

       cp secret_config_sample.py secret_config.py        # Linux/macOS
       copy secret_config_sample.py secret_config.py      # Windows

2. Edita ``secret_config.py`` y reemplaza los valores de ejemplo por
   los de TU servidor PostgreSQL (local o remoto como Render / Neon).

3. NUNCA subas ``secret_config.py`` a GitHub: contiene tu contraseña.
   Ya está incluido en ``.gitignore``. Este archivo de muestra
   (``secret_config_sample.py``) sí se versiona, y por eso solo debe
   tener valores de ejemplo.
"""

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "incapacidades"
DB_USER = "usuario"
DB_PASSWORD = "cambia_esta_clave"
