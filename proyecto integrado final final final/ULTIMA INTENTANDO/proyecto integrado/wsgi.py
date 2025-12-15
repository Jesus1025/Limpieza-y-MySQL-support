# ============================================================
# WSGI - PythonAnywhere
# ============================================================
# Este archivo es el punto de entrada para PythonAnywhere
# Configurar la ruta en Web -> WSGI configuration file
# ============================================================

import sys
import os

# Ruta del proyecto en PythonAnywhere
# CAMBIAR SI ES NECESARIO según tu usuario
project_home = '/home/Teknetautest/proyecto_integrado'

# Agregar al path de Python
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ============================================================
# VARIABLES DE ENTORNO PARA MYSQL
# ============================================================
os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'Teknetautest.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'Teknetautest'
os.environ['MYSQL_PASSWORD'] = '19101810Aa'
os.environ['MYSQL_DATABASE'] = 'Teknetautest$default'
os.environ['SECRET_KEY'] = 'teknetau_produccion_secretkey_2025_seguro'

# ============================================================
# IMPORTAR LA APLICACIÓN FLASK
# ============================================================
from app import app as application

# ============================================================
# LOGGING (opcional, para debug)
# ============================================================
print("="*60)
print("WSGI CARGADO CORRECTAMENTE")
print(f"Project Home: {project_home}")
print(f"MySQL Host: {os.environ.get('MYSQL_HOST')}")
print(f"MySQL User: {os.environ.get('MYSQL_USER')}")
print(f"MySQL DB: {os.environ.get('MYSQL_DATABASE')}")
print("="*60)
