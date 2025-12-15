# ✅ CONFIGURAR MYSQL EN PYTHONANYWHERE

## 🔴 PASO 1: Obtener credenciales MySQL en PythonAnywhere

1. Abre https://www.pythonanywhere.com
2. Login con tu cuenta
3. Ve a **Databases** en el menú superior
4. Busca la sección **MySQL** 
5. Deberías ver algo como:

```
Hostname: tu_usuario.mysql.pythonanywhere-services.com
Username: tu_usuario
Password: [contraseña que configuraste]
Database: tu_usuario$nombre_base_datos
```

**IMPORTANTE:** Copia y guarda estos valores - los necesitaremos

---

## 🔵 PASO 2: Actualizar variables de entorno en wsgi.py

Abre en PythonAnywhere → Files → `/var/www/tu_usuario_pythonanywhere_com_wsgi.py`

Busca estas líneas:

```python
os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'tu_contraseña_mysql'
os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'
```

**REEMPLAZA con tus valores reales:**

```python
os.environ['MYSQL_HOST'] = 'TU_USUARIO.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'TU_USUARIO'
os.environ['MYSQL_PASSWORD'] = 'TU_CONTRASEÑA_AQUI'
os.environ['MYSQL_DATABASE'] = 'TU_USUARIO$tu_base_datos'
```

**Ejemplo (ficticio):**
```python
os.environ['MYSQL_HOST'] = 'juan.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'juan'
os.environ['MYSQL_PASSWORD'] = 'abc123xyz456'
os.environ['MYSQL_DATABASE'] = 'juan$teknetau_db'
```

---

## 🟣 PASO 3: Crear la base de datos MySQL

1. Ve a **Databases** en PythonAnywhere
2. Busca **Create a new database**
3. Ingresa el nombre: `teknetau_db`
4. Click **Create**

---

## 🟡 PASO 4: Crear las tablas en MySQL

En PythonAnywhere, abre **Bash Console**

```bash
# Conectar a MySQL
mysql -h TU_USUARIO.mysql.pythonanywhere-services.com -u TU_USUARIO -p
# Ingresa contraseña cuando te pida

# Una vez conectado (verás mysql>):
USE tu_usuario$teknetau_db;

# Copiar y pegar TODO esto:
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'usuario',
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
);

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
);

# Verificar que se crearon
SHOW TABLES;
DESCRIBE clientes;

# Salir
EXIT;
```

---

## 🟢 PASO 5: Recargar la app en PythonAnywhere

1. Ve a **Web** en PythonAnywhere
2. Busca **Python application** 
3. Click el botón **Reload** (rojo)
4. Espera 10 segundos

---

## 🔍 PASO 6: Verificar que funciona

Abre tu app:
```
https://tu_usuario.pythonanywhere.com
```

### Prueba 1: Agregar cliente

```
1. Click en "Clientes"
2. Click en "+ Nuevo Cliente"
3. Rellena:
   - RUT: 76.660.180-4
   - Razon Social: TEST WINPY
   - Email: test@test.com
4. Click "Guardar"
```

**Resultado esperado:** ✅ "Cliente creado correctamente"

### Prueba 2: Verificar en base de datos

En **Bash Console**:

```bash
mysql -h TU_USUARIO.mysql.pythonanywhere-services.com -u TU_USUARIO -p
# Ingresa contraseña

USE tu_usuario$teknetau_db;
SELECT * FROM clientes;
```

Deberías ver el cliente que acabas de crear ✅

---

## ❌ SI FALLA: Debugging

### Error: "Access denied for user"

**Causa:** Credenciales MySQL incorrectas

**Solución:**
```bash
# Verificar credenciales:
mysql -h tu_usuario.mysql.pythonanywhere-services.com -u tu_usuario -p
# Si te pide contraseña, ingresa la correcta
# Si falla, revisa en PythonAnywhere → Databases
```

### Error: "No module named 'MySQLdb'"

**Causa:** PyMySQL no está instalado

**Solución (en Bash Console):**
```bash
pip install PyMySQL
# O en tu virtualenv:
/home/tu_usuario/.virtualenvs/tu_venv/bin/pip install PyMySQL
```

### Error: "Table 'xyz' doesn't exist"

**Causa:** Las tablas no se crearon

**Solución:**
- Repite PASO 4 (crear tablas)
- Verifica en MySQL que las tablas existan:
  ```bash
  mysql -h ... -u ... -p
  USE tu_usuario$teknetau_db;
  SHOW TABLES;
  ```

### Error: "Lost connection to MySQL server"

**Causa:** Timeout en conexión

**Solución:**
- Aumenta timeout en MYSQL_CONFIG:
  ```python
  MYSQL_CONFIG = {
      ...
      'connect_timeout': 60,
  }
  ```

---

## 📋 CHECKLIST FINAL

- [ ] Credentials obtenidas de PythonAnywhere → Databases
- [ ] wsgi.py actualizado con credenciales correctas
- [ ] Base de datos creada en MySQL
- [ ] Tablas creadas con bash console
- [ ] Web app recargada (Reload button)
- [ ] Probé agregar un cliente ✅
- [ ] Verificué en MySQL que se guardó ✅
- [ ] Todo funciona

---

## 🚀 VALORES DE EJEMPLO (SOLO REFERENCIA)

```
Hostname: juan.mysql.pythonanywhere-services.com
Username: juan
Password: password123abc
Database: juan$teknetau
```

**wsgi.py quedaría:**
```python
os.environ['MYSQL_HOST'] = 'juan.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'juan'
os.environ['MYSQL_PASSWORD'] = 'password123abc'
os.environ['MYSQL_DATABASE'] = 'juan$teknetau'
```

---

## 📞 Si algo sigue sin funcionar:

1. Revisa el **Error log** en PythonAnywhere → Web
2. Copia el error exacto y comparte
3. Verifica que todas las credenciales sean correctas
4. Asegúrate que MySQL está habilitado en tu cuenta PythonAnywhere

