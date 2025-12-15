"""
=============================================================
SCRIPT PARA CREAR TABLAS EN MYSQL - PythonAnywhere
=============================================================
INSTRUCCIONES:
1. Ve a PythonAnywhere -> Databases -> MySQL
2. Abre una consola MySQL
3. Copia y ejecuta el SQL de abajo
=============================================================
"""

# ============================================================
# COPIA ESTE SQL EN LA CONSOLA MYSQL DE PYTHONANYWHERE
# ============================================================

SQL_CREAR_TABLAS = """
-- ============================================================
-- TEKNETAU - Script de creación de tablas MySQL
-- Ejecutar en: Teknetautest$default
-- ============================================================

-- Usar la base de datos correcta
USE Teknetautest$default;

-- ============================================================
-- TABLA: usuarios
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(200),
    email VARCHAR(150),
    rol VARCHAR(50) DEFAULT 'usuario',
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLA: clientes
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rut VARCHAR(20) UNIQUE NOT NULL,
    razon_social VARCHAR(200) NOT NULL,
    giro VARCHAR(150),
    telefono VARCHAR(30),
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLA: proyectos
-- ============================================================
CREATE TABLE IF NOT EXISTS proyectos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    cliente_rut VARCHAR(20),
    presupuesto DECIMAL(15, 2) DEFAULT 0,
    fecha_inicio DATE,
    fecha_termino DATE,
    estado VARCHAR(50) DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_codigo (codigo),
    INDEX idx_cliente (cliente_rut),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLA: documentos
-- ============================================================
CREATE TABLE IF NOT EXISTS documentos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    numero_doc INT NOT NULL,
    tipo_doc VARCHAR(10) NOT NULL,
    fecha_emision DATE NOT NULL,
    cliente_rut VARCHAR(20),
    descripcion TEXT,
    valor_neto DECIMAL(15, 2) DEFAULT 0,
    iva DECIMAL(15, 2) DEFAULT 0,
    valor_total DECIMAL(15, 2) DEFAULT 0,
    estado VARCHAR(50) DEFAULT 'Pendiente',
    forma_pago VARCHAR(50) DEFAULT 'Contado',
    proyecto_codigo VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tipo (tipo_doc),
    INDEX idx_estado (estado),
    INDEX idx_cliente (cliente_rut),
    INDEX idx_proyecto (proyecto_codigo),
    INDEX idx_fecha (fecha_emision)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- INSERTAR USUARIO ADMIN POR DEFECTO
-- Password: admin123
-- ============================================================
INSERT IGNORE INTO usuarios (username, password_hash, nombre, email, rol, activo)
VALUES (
    'admin',
    'pbkdf2:sha256:600000$xK8yR4nT$c8f7d3a2e1b5f9c4d7e2a3b6f8c1d4e7a9b2c5f8e1d4a7b0c3f6e9d2a5b8c1',
    'Administrador',
    'admin@teknetau.cl',
    'admin',
    1
);

-- ============================================================
-- VERIFICAR TABLAS CREADAS
-- ============================================================
SHOW TABLES;

-- Mostrar estructura de cada tabla
DESCRIBE usuarios;
DESCRIBE clientes;
DESCRIBE proyectos;
DESCRIBE documentos;

SELECT 'Tablas creadas correctamente!' as resultado;
"""

# ============================================================
# ALTERNATIVA: Ejecutar desde Python
# ============================================================

def crear_tablas():
    """
    Ejecutar este script desde la consola de PythonAnywhere:
    python create_mysql_tables.py
    """
    import pymysql
    
    config = {
        'host': 'Teknetautest.mysql.pythonanywhere-services.com',
        'user': 'Teknetautest',
        'password': '19101810Aa',
        'database': 'Teknetautest$default',
        'charset': 'utf8mb4',
    }
    
    print("Conectando a MySQL...")
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    print("Creando tabla usuarios...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nombre VARCHAR(200),
            email VARCHAR(150),
            rol VARCHAR(50) DEFAULT 'usuario',
            activo TINYINT(1) DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')
    
    print("Creando tabla clientes...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INT PRIMARY KEY AUTO_INCREMENT,
            rut VARCHAR(20) UNIQUE NOT NULL,
            razon_social VARCHAR(200) NOT NULL,
            giro VARCHAR(150),
            telefono VARCHAR(30),
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')
    
    print("Creando tabla proyectos...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id INT PRIMARY KEY AUTO_INCREMENT,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            descripcion TEXT,
            cliente_rut VARCHAR(20),
            presupuesto DECIMAL(15, 2) DEFAULT 0,
            fecha_inicio DATE,
            fecha_termino DATE,
            estado VARCHAR(50) DEFAULT 'Activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_codigo (codigo),
            INDEX idx_cliente (cliente_rut),
            INDEX idx_estado (estado)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')
    
    print("Creando tabla documentos...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INT PRIMARY KEY AUTO_INCREMENT,
            numero_doc INT NOT NULL,
            tipo_doc VARCHAR(10) NOT NULL,
            fecha_emision DATE NOT NULL,
            cliente_rut VARCHAR(20),
            descripcion TEXT,
            valor_neto DECIMAL(15, 2) DEFAULT 0,
            iva DECIMAL(15, 2) DEFAULT 0,
            valor_total DECIMAL(15, 2) DEFAULT 0,
            estado VARCHAR(50) DEFAULT 'Pendiente',
            forma_pago VARCHAR(50) DEFAULT 'Contado',
            proyecto_codigo VARCHAR(50),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_tipo (tipo_doc),
            INDEX idx_estado (estado),
            INDEX idx_cliente (cliente_rut),
            INDEX idx_proyecto (proyecto_codigo),
            INDEX idx_fecha (fecha_emision)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')
    
    print("Creando usuario admin...")
    from werkzeug.security import generate_password_hash
    pwd_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
    
    try:
        cursor.execute('''
            INSERT INTO usuarios (username, password_hash, nombre, email, rol, activo)
            VALUES (%s, %s, %s, %s, %s, 1)
        ''', ('admin', pwd_hash, 'Administrador', 'admin@teknetau.cl', 'admin'))
    except pymysql.err.IntegrityError:
        print("Usuario admin ya existe, actualizando password...")
        cursor.execute('''
            UPDATE usuarios SET password_hash = %s WHERE username = 'admin'
        ''', (pwd_hash,))
    
    conn.commit()
    
    # Verificar
    print("\n=== TABLAS CREADAS ===")
    cursor.execute("SHOW TABLES")
    for table in cursor.fetchall():
        print(f"  - {table[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    print(f"\nUsuarios en BD: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM clientes")
    print(f"Clientes en BD: {cursor.fetchone()[0]}")
    
    conn.close()
    print("\n¡Tablas creadas correctamente!")
    print("Usuario: admin")
    print("Password: admin123")


if __name__ == '__main__':
    print("="*60)
    print("CREADOR DE TABLAS MYSQL PARA PYTHONANYWHERE")
    print("="*60)
    crear_tablas()
