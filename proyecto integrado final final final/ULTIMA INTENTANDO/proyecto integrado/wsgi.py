# Archivo WSGI para PythonAnywhere
# Este archivo es el punto de entrada para el servidor web

import sys
import os

# Agregar el directorio del proyecto al path de Python
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ============================================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO PARA PYTHONANYWHERE
# ============================================================

if not os.environ.get('ENVIRONMENT'):
    os.environ['ENVIRONMENT'] = 'production'

if not os.environ.get('MYSQL_HOST'):
    os.environ['MYSQL_HOST'] = 'Teknetautest.mysql.pythonanywhere-services.com'

if not os.environ.get('MYSQL_USER'):
    os.environ['MYSQL_USER'] = 'Teknetautest'

if not os.environ.get('MYSQL_PASSWORD'):
    # IMPORTANTE: Reemplaza esto con tu contraseña MySQL
    os.environ['MYSQL_PASSWORD'] = '19101810Aa'

if not os.environ.get('MYSQL_DATABASE'):
    os.environ['MYSQL_DATABASE'] = 'Teknetautest$default'

if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'tu_clave_secreta_aqui_2025'

# ============================================================
# Importar la aplicación Flask
from app import app as application

# Para PythonAnywhere, la variable debe llamarse 'application'
# Si prefieres usar otro nombre, puedes configurarlo en el panel de control

# Log de configuración (solo para debugging)
print("=" * 60)
print("CONFIGURACIÓN WSGI CARGADA")
print("=" * 60)
print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT')}")
print(f"MYSQL_HOST: {os.environ.get('MYSQL_HOST')}")
print(f"MYSQL_USER: {os.environ.get('MYSQL_USER')}")
print(f"MYSQL_DATABASE: {os.environ.get('MYSQL_DATABASE')}")
print("=" * 60)
