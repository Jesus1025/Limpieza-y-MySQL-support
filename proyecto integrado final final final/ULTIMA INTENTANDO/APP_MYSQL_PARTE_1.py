# ============================================================
# CÓDIGO ACTUALIZADO PARA app.py CON SOPORTE MYSQL
# ============================================================
# 
# Reemplaza los primeros 50 líneas de tu app.py con esto:
#

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, Response
import sqlite3
import os
import hashlib
import re
import io
import csv
from functools import wraps
from datetime import datetime, timedelta
from urllib.parse import quote_plus

# Para MySQL
try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'teknetau_dev_key_cambiar_en_produccion_2025')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Crear directorios
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'), exist_ok=True)

# ============================================================
# DETECCIÓN DE ENTORNO Y CONFIGURACIÓN DE BD
# ============================================================

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development').lower()
USE_MYSQL = (ENVIRONMENT == 'production' and HAS_PYMYSQL)

# Función para obtener conexión a BD
if USE_MYSQL:
    print("🔌 Usando MySQL en producción")
    
    def get_db_connection():
        """Conexión a MySQL para PythonAnywhere"""
        try:
            conn = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', ''),
                database=os.environ.get('MYSQL_DATABASE', 'teknetau'),
                charset='utf8mb4',
                autocommit=True
            )
            return conn
        except Exception as e:
            print(f"❌ Error conectando a MySQL: {e}")
            # Fallback a SQLite
            print("⚠️ Usando SQLite como fallback")
            return get_sqlite_connection()
    
    def get_sqlite_connection():
        """Fallback a SQLite"""
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'teknetau.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
else:
    print("💾 Usando SQLite en desarrollo")
    
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'teknetau.db')
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    def get_db_connection():
        """Conexión a SQLite para desarrollo"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

# ============================================================
# UTILIDADES PARA TRABAJAR CON BD
# ============================================================

def rows_to_dicts(rows):
    """Convierte resultados de BD a diccionarios (compatible SQLite y MySQL)"""
    if not rows:
        return []
    
    result = []
    for row in rows:
        if isinstance(row, dict):
            # MySQL con DictCursor
            result.append(row)
        elif isinstance(row, sqlite3.Row):
            # SQLite
            result.append(dict(row))
        else:
            # Tupla o lista
            result.append(row)
    
    return result

def normalize_rut(rut):
    """Normaliza RUT chileno"""
    if not rut:
        return None
    rut = re.sub(r'[^0-9k]', '', str(rut).lower()).upper()
    if len(rut) >= 2:
        return f"{rut[:-1]}-{rut[-1]}"
    return rut

def validate_rut(rut):
    """Valida RUT chileno"""
    if not rut or '-' not in str(rut):
        return False
    try:
        rut_parts = str(rut).upper().split('-')
        body, dv = rut_parts[0].replace('.', ''), rut_parts[1]
        
        if not body.isdigit() or len(dv) != 1:
            return False
        
        s = sum(int(digit) * (2 + (i % 6)) for i, digit in enumerate(reversed(body)))
        expected_dv = str(11 - (s % 11))
        expected_dv = '0' if expected_dv == '11' else 'K' if expected_dv == '10' else expected_dv
        
        return expected_dv == dv
    except:
        return False

# ============================================================
# DECORADOR DE LOGIN
# ============================================================

def login_required(f):
    """Decorador para verificar login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_roles):
    """Decorador para verificar rol del usuario"""
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'success': False, 'error': 'No autenticado'}), 401
            
            user_role = session.get('rol', 'usuario')
            if user_role not in required_roles:
                return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================
# EL RESTO DE app.py SIGUE IGUAL...
# ============================================================
#
# Solo los primeros 100+ líneas necesitan cambios
# El resto del código (rutas, templates, etc.) funciona igual
# tanto con SQLite como con MySQL
#
