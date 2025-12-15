# 🚀 GUÍA COMPLETA: FLASK + MySQL EN PYTHONYWHERE

## PASO 1: PREPARACIÓN EN PYTHONYWHERE

### 1.1 Registrarse en PythonAnywhere
1. Ir a https://www.pythonanywhere.com
2. Click en "Sign up for a free account"
3. Completar registro (recomendado con GitHub para facilitar despliegue)

### 1.2 Crear base de datos MySQL
En el panel de control de PythonAnywhere:

1. Click en la pestaña **Databases**
2. Click en **Add a new database**
3. Seleccionar **MySQL**
4. Nombre: `teknetau_db`
5. Contraseña: Crear una fuerte (guardar para después)
6. Click en **Create**

**Datos importantes que aparecerán:**
```
Nombre de BD: username$teknetau_db
Usuario: username
Contraseña: [la que creaste]
Host: username.mysql.pythonanywhere-services.com
Puerto: 3306
```

---

## PASO 2: CREAR ARCHIVO DE CONFIGURACIÓN MYSQL

### 2.1 Crear `config_mysql.py` en tu proyecto

```python
# config_mysql.py
import os
from urllib.parse import quote_plus

class MySQLConfig:
    """Configuración para MySQL en PythonAnywhere"""
    
    # Variables de entorno (usar en PythonAnywhere)
    MYSQL_USER = os.environ.get('MYSQL_USER', 'tu_usuario')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'tu_contraseña')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'tu_usuario.mysql.pythonanywhere-services.com')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'tu_usuario$teknetau_db')
    
    # Para desarrollo local (SQLite)
    # Para producción (MySQL en PythonAnywhere)
    if os.environ.get('ENVIRONMENT') == 'production':
        # URL para MySQL con PyMySQL
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@"
            f"{MYSQL_HOST}/{MYSQL_DATABASE}?charset=utf8mb4"
        )
    else:
        # URL para SQLite (desarrollo)
        SQLALCHEMY_DATABASE_URI = "sqlite:///database/teknetau.db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

class Config:
    """Configuración general de la app"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'teknetau-dev-key-2025')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### 2.2 Actualizar `requirements.txt`

```
Flask>=2.0.0
werkzeug>=2.0.0
openpyxl>=3.0.0
PyMySQL>=1.0.2
mysql-connector-python>=8.0.33
```

---

## PASO 3: MODIFICAR `app.py` PARA MYSQL

### 3.1 Cambios en las importaciones y configuración inicial

**Reemplazar esta sección al inicio de app.py:**

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, Response
import sqlite3
import os
import hashlib
import re
import io
import csv
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'teknetau_dev_key_cambiar_en_produccion_2025')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Crear directorios necesarios
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'), exist_ok=True)

# ============================================================
# DETECTAR ENTORNO Y CONFIGURAR BASE DE DATOS
# ============================================================

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    # USAR MYSQL EN PYTHONYWHERE
    try:
        import pymysql
        
        # Conexión a MySQL
        def get_db_connection():
            conn = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'tu_usuario.mysql.pythonanywhere-services.com'),
                user=os.environ.get('MYSQL_USER', 'tu_usuario'),
                password=os.environ.get('MYSQL_PASSWORD', 'tu_contraseña'),
                database=os.environ.get('MYSQL_DATABASE', 'tu_usuario$teknetau_db'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return conn
    except ImportError:
        print("PyMySQL no está instalado. Usar SQLite como fallback.")
        import sqlite3
        DATABASE = 'database/teknetau.db'
        def get_db_connection():
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            return conn
else:
    # USAR SQLITE PARA DESARROLLO
    import sqlite3
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'teknetau.db')
    
    def get_db_connection():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

# Crear carpeta de base de datos si no existe
os.makedirs(os.path.dirname(DATABASE) if ENVIRONMENT == 'development' else '.', exist_ok=True)
```

### 3.2 Agregar función para inicializar BD MySQL

```python
def init_mysql_database():
    """Inicializa la base de datos MySQL con las tablas necesarias"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # TABLA USUARIOS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(200),
                email VARCHAR(100),
                rol VARCHAR(50) DEFAULT 'admin',
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # TABLA CLIENTES
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INT PRIMARY KEY AUTO_INCREMENT,
                rut VARCHAR(20) UNIQUE,
                razon_social VARCHAR(200),
                giro VARCHAR(200),
                telefono VARCHAR(20),
                email VARCHAR(100),
                direccion VARCHAR(300),
                comuna VARCHAR(100),
                cuenta_corriente VARCHAR(50),
                banco VARCHAR(100),
                observaciones TEXT,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # TABLA PROYECTOS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proyectos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                codigo VARCHAR(50) UNIQUE,
                nombre VARCHAR(200),
                descripcion TEXT,
                cliente_rut VARCHAR(20),
                presupuesto DECIMAL(12,2),
                fecha_inicio DATE,
                fecha_termino DATE,
                estado VARCHAR(50),
                FOREIGN KEY (cliente_rut) REFERENCES clientes(rut)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # TABLA DOCUMENTOS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                numero_doc INT,
                tipo_doc VARCHAR(10),
                fecha_emision DATE,
                cliente_rut VARCHAR(20),
                descripcion TEXT,
                valor_neto DECIMAL(12,2),
                iva DECIMAL(12,2),
                valor_total DECIMAL(12,2),
                estado VARCHAR(50) DEFAULT 'Pendiente',
                forma_pago VARCHAR(50),
                proyecto_codigo VARCHAR(50),
                FOREIGN KEY (cliente_rut) REFERENCES clientes(rut)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        conn.commit()
        print("✅ Base de datos MySQL inicializada correctamente")
        
    except Exception as e:
        print(f"❌ Error inicializando BD MySQL: {e}")
        # Intentar con SQLite como fallback
        init_sqlite_database()
    finally:
        conn.close()
```

---

## PASO 4: CREAR ARCHIVO `deploy.sh` PARA PYTHONYWHERE

```bash
#!/bin/bash
# deploy.sh - Script para desplegar en PythonAnywhere

# Variables de entorno para MySQL
export ENVIRONMENT=production
export MYSQL_HOST=tu_usuario.mysql.pythonanywhere-services.com
export MYSQL_USER=tu_usuario
export MYSQL_PASSWORD=tu_contraseña
export MYSQL_DATABASE=tu_usuario$teknetau_db
export SECRET_KEY=tu_clave_secreta_fuerte
export FLASK_ENV=production

# Actualizar dependencias
pip install --user -r requirements.txt

# Inicializar base de datos
python -c "from app import init_mysql_database; init_mysql_database()"

# Recargar aplicación web
touch /var/www/tu_usuario_pythonanywhere_com_wsgi.py

echo "✅ Despliegue completado"
```

---

## PASO 5: ACTUALIZAR WSGI PARA PYTHONYWHERE

```python
# wsgi.py - Punto de entrada para PythonAnywhere

import sys
import os
from pathlib import Path

# Variables de entorno para producción
os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'tu_usuario.mysql.pythonanywhere-services.com')
os.environ['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'tu_usuario')
os.environ['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'tu_contraseña')
os.environ['MYSQL_DATABASE'] = os.environ.get('MYSQL_DATABASE', 'tu_usuario$teknetau_db')
os.environ['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta')
os.environ['FLASK_ENV'] = 'production'

# Agregar proyecto al path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importar app
from app import app as application
```

---

## PASO 6: CONFIGURAR EN PYTHONAWARE DASHBOARD

### 6.1 Descargar y subir código

1. Ir a **Web** → **Add a new web app**
2. Seleccionar **Python 3.10** (o la versión que uses)
3. Seleccionar **Flask**

### 6.2 Configurar variables de entorno

En el archivo `/var/www/tu_usuario_pythonanywhere_com_wsgi.py` (genera PythonAnywhere):

Editar y agregar antes de `from app import application`:

```python
import os
os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'tu_contraseña_mysql'
os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'
os.environ['SECRET_KEY'] = 'una_clave_super_secreta_aqui'
os.environ['FLASK_ENV'] = 'production'
```

### 6.3 Subir requirements.txt

1. Ir a **Web**
2. Bajar hasta **Virtualenv**
3. Hacer click en la ruta del virtualenv
4. Ejecutar: `pip install -r /home/tu_usuario/mysite/requirements.txt`

---

## PASO 7: MIGRAR DATOS DE SQLITE A MYSQL

### 7.1 Script de migración

```python
# migrate_db.py
import sqlite3
import pymysql
import os

# Conexión SQLite
sqlite_conn = sqlite3.connect('database/teknetau.db')
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# Conexión MySQL
mysql_conn = pymysql.connect(
    host=os.environ.get('MYSQL_HOST'),
    user=os.environ.get('MYSQL_USER'),
    password=os.environ.get('MYSQL_PASSWORD'),
    database=os.environ.get('MYSQL_DATABASE'),
    charset='utf8mb4'
)
mysql_cursor = mysql_conn.cursor()

# Tablas a migrar
TABLES = ['usuarios', 'clientes', 'proyectos', 'documentos']

for table in TABLES:
    print(f"Migrando tabla {table}...")
    
    # Obtener datos de SQLite
    sqlite_cursor.execute(f"SELECT * FROM {table}")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"  - {table} está vacía")
        continue
    
    # Obtener columnas
    columns = [description[0] for description in sqlite_cursor.description]
    
    # Insertar en MySQL
    for row in rows:
        placeholders = ','.join(['%s'] * len(columns))
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        try:
            mysql_cursor.execute(sql, tuple(row))
        except Exception as e:
            print(f"  ⚠️ Error en fila: {e}")
            continue
    
    mysql_conn.commit()
    print(f"  ✅ {table} migrada ({len(rows)} registros)")

print("\n✅ Migración completada")

sqlite_conn.close()
mysql_conn.close()
```

**Ejecutar:**
```bash
python migrate_db.py
```

---

## PASO 8: VERIFICAR CONEXIÓN

### 8.1 Script de prueba

```python
# test_mysql_connection.py
import os
import pymysql

try:
    conn = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'tu_usuario.mysql.pythonanywhere-services.com'),
        user=os.environ.get('MYSQL_USER', 'tu_usuario'),
        password=os.environ.get('MYSQL_PASSWORD', 'tu_contraseña'),
        database=os.environ.get('MYSQL_DATABASE', 'tu_usuario$teknetau_db'),
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]
    
    print(f"✅ Conexión exitosa!")
    print(f"   Usuarios en BD: {count}")
    
    conn.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")
```

**Ejecutar:**
```bash
python test_mysql_connection.py
```

---

## PASO 9: CHECKLIST FINAL

- [ ] BD MySQL creada en PythonAnywhere
- [ ] Archivo `config_mysql.py` creado
- [ ] `requirements.txt` actualizado con PyMySQL
- [ ] `app.py` modificado para soportar MySQL
- [ ] `wsgi.py` actualizado
- [ ] Código subido a PythonAnywhere
- [ ] Variables de entorno configuradas
- [ ] Datos migrados de SQLite a MySQL
- [ ] Conexión a MySQL probada
- [ ] Aplicación recargada en PythonAnywhere

---

## PROBLEMAS COMUNES Y SOLUCIONES

### "Access denied for user 'username'@'...' to database"
```
Solución: Verificar contraseña y nombre de BD en variables de entorno
BD debe ser: username$teknetau_db (no solo teknetau_db)
```

### "Lost connection to MySQL server"
```
Solución: Agregar en config:
'pool_pre_ping': True,
'pool_recycle': 3600,
```

### "Charset utf8mb4 not supported"
```
Solución: Agregar charset en URL:
mysql+pymysql://user:pass@host/db?charset=utf8mb4
```

### Timeout en uploads
```
Solución: En PythonAnywhere ir a Web → Timeout → Aumentar a 300s
```

---

## REFERENCIAS

- [PythonAnywhere Docs](https://help.pythonanywhere.com/)
- [Flask MySQL Guide](https://flask.palletsprojects.com/)
- [PyMySQL Docs](https://pymysql.readthedocs.io/)

---

**¡Listo! Tu aplicación está lista para MySQL en PythonAnywhere** 🚀

