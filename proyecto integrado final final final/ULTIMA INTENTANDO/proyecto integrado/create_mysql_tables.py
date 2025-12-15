#!/usr/bin/env python
"""
Script para crear todas las tablas necesarias en MySQL en PythonAnywhere
Ejecuta esto en Bash Console de PythonAnywhere
"""
import os
import sys

# Configurar variables de entorno (son las de wsgi.py)
os.environ['MYSQL_HOST'] = 'Teknetautest.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'Teknetautest'
os.environ['MYSQL_PASSWORD'] = '19101810Aa'
os.environ['MYSQL_DATABASE'] = 'Teknetautest$default'

try:
    import MySQLdb
except ImportError:
    print("Instalando MySQLdb...")
    os.system('pip install mysqlclient')
    import MySQLdb

# Configuración
MYSQL_CONFIG = {
    'host': 'Teknetautest.mysql.pythonanywhere-services.com',
    'user': 'Teknetautest',
    'passwd': '19101810Aa',
    'db': 'Teknetautest$default'
}

print("🔗 Conectando a MySQL...")
conn = MySQLdb.connect(**MYSQL_CONFIG)
cursor = conn.cursor()

# SQL para crear tabla clientes
sql_clientes = '''
CREATE TABLE IF NOT EXISTS clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rut VARCHAR(20) UNIQUE NOT NULL,
    razon_social VARCHAR(200) NOT NULL,
    giro VARCHAR(150),
    telefono VARCHAR(20),
    email VARCHAR(150),
    direccion VARCHAR(300),
    comuna VARCHAR(100),
    cuenta_corriente VARCHAR(50),
    banco VARCHAR(100),
    observaciones TEXT,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rut (rut),
    INDEX idx_activo (activo)
) CHARACTER SET utf8mb4
'''

# SQL para crear tabla usuarios
sql_usuarios = '''
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(200),
    email VARCHAR(150),
    rol VARCHAR(50) DEFAULT 'admin',
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4
'''

# SQL para crear tabla documentos
sql_documentos = '''
CREATE TABLE IF NOT EXISTS documentos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    numero_doc INTEGER,
    tipo_doc VARCHAR(50),
    fecha_emision DATE,
    cliente_rut VARCHAR(20),
    descripcion TEXT,
    valor_neto DECIMAL(12, 2),
    iva DECIMAL(12, 2),
    valor_total DECIMAL(12, 2),
    estado VARCHAR(50) DEFAULT 'Pendiente',
    forma_pago VARCHAR(50),
    proyecto_codigo VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cliente (cliente_rut),
    INDEX idx_estado (estado)
) CHARACTER SET utf8mb4
'''

try:
    print("📝 Creando tabla clientes...")
    cursor.execute(sql_clientes)
    print("✅ Tabla clientes creada/verificada")
    
    print("📝 Creando tabla usuarios...")
    cursor.execute(sql_usuarios)
    print("✅ Tabla usuarios creada/verificada")
    
    print("📝 Creando tabla documentos...")
    cursor.execute(sql_documentos)
    print("✅ Tabla documentos creada/verificada")
    
    # Insertar usuario admin si no existe
    print("📝 Insertando usuario admin...")
    from werkzeug.security import generate_password_hash
    pwd = generate_password_hash('admin123', method='pbkdf2:sha256')
    cursor.execute(
        'INSERT IGNORE INTO usuarios (username, password_hash, nombre, rol) VALUES (%s, %s, %s, %s)',
        ('admin', pwd, 'Administrador', 'admin')
    )
    print("✅ Usuario admin insertado (si no existía)")
    
    conn.commit()
    print("\n✅ TODAS LAS TABLAS CREADAS EXITOSAMENTE")
    
    # Verificar tablas creadas
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("\n📊 Tablas en la BD:")
    for table in tables:
        print(f"   - {table[0]}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
