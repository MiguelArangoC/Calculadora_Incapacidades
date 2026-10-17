"""
Plantilla de configuración de la base de datos.

INSTRUCCIONES DE USO
--------------------
1. Copia este archivo con el nombre ``secret_config.py`` en la misma
   carpeta (la raíz del proyecto, junto a ``main.py``):

       cp secret_config_sample.py secret_config.py        # Linux/macOS
       copy secret_config_sample.py secret_config.py      # Windows

2. Edita ``secret_config.py`` y reemplaza los valores de ejemplo por
   los de TU servidor de base de datos.

3. NUNCA subas ``secret_config.py`` a GitHub: contiene tu contraseña.
   Ya está incluido en ``.gitignore``. Este archivo de muestra
   (``secret_config_sample.py``) sí se versiona, y por eso solo debe
   tener valores de ejemplo.

OPCIONES DE MOTOR
-----------------
PostgreSQL (requiere:  pip install psycopg2-binary):
    DB_DRIVER = "postgresql+psycopg2"      DB_PORT = 5432

MySQL / MariaDB (requiere:  pip install pymysql):
    DB_DRIVER = "mysql+pymysql"            DB_PORT = 3306

SQLite (archivo local, no necesita servidor ni usuario):
    DB_DRIVER = "sqlite"
    DB_NAME = "incapacidades.db"
    DB_USER = DB_PASSWORD = DB_HOST = DB_PORT = None

Si ``secret_config.py`` no existe, el programa usa por defecto un
archivo SQLite local llamado ``incapacidades.db``.
"""

DB_DRIVER = "postgresql+psycopg2"
DB_USER = "usuario"
DB_PASSWORD = "cambia_esta_clave"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "incapacidades"
