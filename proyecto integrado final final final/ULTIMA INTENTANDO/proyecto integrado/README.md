# TEKNETAU - Sistema de Gestión

## Despliegue en PythonAnywhere

### Paso 1: Subir archivos

1. Ve a **PythonAnywhere** -> **Files**
2. Crea la carpeta `/home/Teknetautest/proyecto_integrado/`
3. Sube estos archivos:
   - `app.py`
   - `wsgi.py`
   - `requirements.txt`
   - `create_mysql_tables.py`
   - Carpeta `templates/` (completa)
   - Carpeta `static/` (completa)

### Paso 2: Crear tablas en MySQL

1. Ve a **Databases** -> **MySQL**
2. Abre **Start a console on Teknetautest$default**
3. Copia y ejecuta este SQL:

```sql
USE Teknetautest$default;

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
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Crear usuario admin (password: admin123)
INSERT INTO usuarios (username, password_hash, nombre, email, rol, activo)
VALUES ('admin', 'pbkdf2:sha256:600000$xK8yR4nT$c8f7d3a2e1b5f9c4d7e2a3b6f8c1d4e7a9b2c5f8e1d4a7b0c3f6e9d2a5b8c1', 'Administrador', 'admin@teknetau.cl', 'admin', 1)
ON DUPLICATE KEY UPDATE nombre = 'Administrador';
```

### Paso 3: Configurar Web App

1. Ve a **Web** -> **Add a new web app**
2. Selecciona **Manual configuration**
3. Selecciona **Python 3.10**
4. Configura:
   - **Source code**: `/home/Teknetautest/proyecto_integrado`
   - **Working directory**: `/home/Teknetautest/proyecto_integrado`
   - **WSGI configuration file**: Edita y reemplaza con el contenido de `wsgi.py`

### Paso 4: Instalar dependencias

1. Abre una **Bash console**
2. Ejecuta:

```bash
cd /home/Teknetautest/proyecto_integrado
pip3 install --user -r requirements.txt
```

### Paso 5: Recargar la aplicación

1. Ve a **Web**
2. Click en **Reload Teknetautest.pythonanywhere.com**

---

## Credenciales por defecto

- **Usuario**: admin
- **Contraseña**: admin123

## Configuración MySQL

- **Host**: Teknetautest.mysql.pythonanywhere-services.com
- **User**: Teknetautest
- **Password**: 19101810Aa
- **Database**: Teknetautest$default

## Archivos principales

- `app.py` - Aplicación Flask principal
- `wsgi.py` - Punto de entrada para PythonAnywhere
- `create_mysql_tables.py` - Script para crear tablas
- `templates/` - Plantillas HTML
- `static/` - CSS y JavaScript
