# 🚀 GUÍA RÁPIDA: AGREGAR CLIENTES EN PYTHONANYWHERE CON MYSQL

## Lo que hizo el agente:

✅ **app.py**: Código detecta automáticamente si estás usando MySQL o SQLite
✅ **wsgi.py**: Configurado para pasar credenciales MySQL

## Lo que DEBES hacer:

### PASO 1️⃣: Obtén tus credenciales MySQL

En PythonAnywhere:
```
Web → MySQL → Data
```

Deberías ver algo así:
```
Hostname: tu_usuario.mysql.pythonanywhere-services.com
Username: tu_usuario
Password: [tu_contraseña]
Database: tu_usuario$nombre_bd
```

### PASO 2️⃣: Actualiza wsgi.py en PythonAnywhere

En PythonAnywhere:
```
Files → /var/www/tu_usuario_pythonanywhere_com_wsgi.py
```

Busca estas 4 líneas y CÁMBIALAS CON TUS VALORES:

```python
os.environ['MYSQL_HOST'] = 'TU_USUARIO.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'TU_USUARIO'
os.environ['MYSQL_PASSWORD'] = 'TU_CONTRASEÑA'
os.environ['MYSQL_DATABASE'] = 'TU_USUARIO$tu_base_de_datos'
```

**EJEMPLO REAL** (cambia TU_USUARIO):
```python
os.environ['MYSQL_HOST'] = 'juan.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'juan'
os.environ['MYSQL_PASSWORD'] = 'abc123xyz'
os.environ['MYSQL_DATABASE'] = 'juan$teknetau_db'
```

**GUARDA** (Ctrl+S)

### PASO 3️⃣: Crea base de datos en MySQL

En PythonAnywhere → Web → Base de datos:
```
Click "Create a new database"
Nombre: teknetau_db
Click Create
```

### PASO 4️⃣: Crea las tablas

En PythonAnywhere → Bash console:

```bash
mysql -h TU_USUARIO.mysql.pythonanywhere-services.com -u TU_USUARIO -p
# Ingresa tu contraseña

# Ahora está conectado a MySQL (verás mysql> )

USE tu_usuario$teknetau_db;

# COPIAR Y PEGAR ESTO COMPLETO:

CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'usuario',
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4;

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
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS documentos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tipo VARCHAR(50) NOT NULL,
    numero INT NOT NULL,
    cliente_id INT NOT NULL,
    fecha DATE NOT NULL,
    descripcion TEXT,
    neto DECIMAL(12,2),
    iva DECIMAL(12,2),
    total DECIMAL(12,2),
    estado VARCHAR(50) DEFAULT 'activo',
    observaciones TEXT,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    INDEX idx_cliente (cliente_id),
    INDEX idx_tipo (tipo),
    INDEX idx_fecha (fecha)
) CHARACTER SET utf8mb4;

# Verificar que se crearon:
SHOW TABLES;

# Salir:
EXIT;
```

### PASO 5️⃣: Recarga la app

En PythonAnywhere:
```
Web → Python [versión] → Reload
```

Espera 10 segundos.

### PASO 6️⃣: Prueba guardar un cliente

Abre: `https://tu_usuario.pythonanywhere.com/clientes`

```
Click "+ Nuevo Cliente"

RUT: 76.660.180-4
Razon Social: TEST WINPY
Email: test@test.com

Click "Guardar"
```

**Resultado esperado:** ✅ "Cliente creado correctamente"

---

## ✅ Verificar en MySQL que se guardó

En Bash Console:

```bash
mysql -h TU_USUARIO.mysql.pythonanywhere-services.com -u TU_USUARIO -p
# Contraseña

USE tu_usuario$teknetau_db;
SELECT * FROM clientes;
```

Deberías ver:
```
id=1, rut=76660180-4, razon_social=TEST WINPY, email=test@test.com
```

✅ ¡LISTO!

---

## ❌ Si no funciona

### Error: "Access denied for user"
→ Verifica que escribiste EXACTO tu usuario y contraseña en wsgi.py

### Error: "Table 'xyz' doesn't exist"
→ Las tablas no se crearon. Repite PASO 4

### Error: "Connection refused"
→ Verifica MYSQL_HOST en wsgi.py

**Copia el error exacto y comparte para debugging**

---

## 📝 Resumen de cambios

| Archivo | Cambio |
|---------|--------|
| **app.py** | ✅ Detecta MySQL automáticamente |
| **wsgi.py** | ✅ Pasa credenciales MySQL |
| **Tu configuración** | 🔴 DEBES hacer esto |

