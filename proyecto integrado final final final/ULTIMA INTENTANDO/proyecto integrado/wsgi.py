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
# IMPORTANTE: Estas variables también deben estar configuradas en:
# PythonAnywhere → Web → Environment variables
# 
# Pero las configuramos aquí como fallback:

if not os.environ.get('ENVIRONMENT'):
    os.environ['ENVIRONMENT'] = 'production'

if not os.environ.get('MYSQL_HOST'):
    # Reemplaza 'tu_usuario' con tu usuario de PythonAnywhere
    os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'

if not os.environ.get('MYSQL_USER'):
    # Reemplaza 'tu_usuario' con tu usuario de PythonAnywhere
    os.environ['MYSQL_USER'] = 'tu_usuario'

if not os.environ.get('MYSQL_PASSWORD'):
    # Reemplaza con tu contraseña de MySQL de PythonAnywhere
    os.environ['MYSQL_PASSWORD'] = 'tu_contraseña_mysql'

if not os.environ.get('MYSQL_DATABASE'):
    # Reemplaza 'tu_usuario$nombre_bd' con tu base de datos en PythonAnywhere
    os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'

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
