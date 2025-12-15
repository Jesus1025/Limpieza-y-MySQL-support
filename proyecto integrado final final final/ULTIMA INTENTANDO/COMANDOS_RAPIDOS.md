# 🖥️ COMANDOS RÁPIDOS - COPIA Y PEGA

## AMBIENTE LOCAL (Desarrollo)

### 1. Instalar dependencias
```bash
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO"
pip install flask werkzeug openpyxl
```

### 2. Ejecutar aplicación localmente
```bash
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO\proyecto integrado"
python app.py
```

Luego abre: http://localhost:5000

### 3. Limpiar archivos innecesarios
```bash
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO"
python cleanup.py
```

### 4. Probar conexión a BD (SQLite)
```bash
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO\proyecto integrado"
python -c "from app import get_db_connection; conn = get_db_connection(); print('✓ Conexión OK')"
```

---

## PYTHONAWARE - BASH/CONSOLA

### 1. En la Consola Bash de PythonAnywhere

**Entrar a tu cuenta, luego:**

```bash
# Ir a tu carpeta de proyecto
cd /home/tu_usuario/mysite

# Clonar o descargar tu código
git clone https://github.com/tu_usuario/tu_repo.git
# O si lo subiste por SFTP, ya estará en lugar

# Crear/activar virtualenv
mkvirtualenv --python=/usr/bin/python3.10 teknetau

# Instalar dependencias
pip install -r requirements.txt

# Verificar que PyMySQL está instalado
pip show pymysql

# Probar conexión a MySQL (opcional)
python -c "import pymysql; print('PyMySQL OK')"
```

### 2. Variables de Entorno en PythonAnywhere

**En el archivo WSGI (`/var/www/tu_usuario_pythonanywhere_com_wsgi.py`):**

```python
import sys
import os

# ========== VARIABLES PARA MYSQL ==========
os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'TU_CONTRASEÑA_MYSQL'
os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'
os.environ['SECRET_KEY'] = 'UNA_CLAVE_SECRETA_SUPER_FUERTE_AQUI_12345'
os.environ['FLASK_ENV'] = 'production'
# ==========================================

project_home = u'/home/tu_usuario/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)
from app import app as application
```

### 3. Crear tablas en MySQL (Bash)

```bash
cd /home/tu_usuario/mysite

# Opción 1: Python
python -c "
import pymysql
import os

os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'TU_PASSWORD'
os.environ['MYSQL_DATABASE'] = 'tu_usuario\$teknetau_db'

from app import init_mysql_database
init_mysql_database()
print('✓ BD MySQL inicializada')
"

# Opción 2: MySQL CLI (si está disponible)
mysql -h tu_usuario.mysql.pythonanywhere-services.com -u tu_usuario -p tu_usuario\$teknetau_db < schema.sql
```

### 4. Recargar aplicación web

En PythonAnywhere Dashboard → Web → **Reload** (botón verde)

O por Bash:
```bash
touch /var/www/tu_usuario_pythonanywhere_com_wsgi.py
```

---

## MIGRACIÓN DE DATOS (Si tienes datos en SQLite)

### Paso 1: Exportar de SQLite
```bash
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO\proyecto integrado"

# Crear archivo SQL desde SQLite
sqlite3 database/teknetau.db .dump > export.sql
```

### Paso 2: Importar a MySQL (en PythonAnywhere Bash)
```bash
# Descargar el archivo export.sql a PythonAnywhere

# Importar
mysql -h tu_usuario.mysql.pythonanywhere-services.com \
      -u tu_usuario \
      -p tu_usuario\$teknetau_db < export.sql
```

### Paso 3: Verificar datos
```bash
mysql -h tu_usuario.mysql.pythonanywhere-services.com \
      -u tu_usuario \
      -p tu_usuario\$teknetau_db

# En el prompt de MySQL:
SELECT COUNT(*) FROM usuarios;
SELECT COUNT(*) FROM clientes;
SELECT COUNT(*) FROM proyectos;
SELECT COUNT(*) FROM documentos;
```

---

## PRUEBAS RÁPIDAS

### Test 1: Verificar app.py es válido
```bash
python -m py_compile "proyecto integrado\app.py"
echo "✓ Sintaxis OK" || echo "✗ Error de sintaxis"
```

### Test 2: Ver versiones instaladas
```bash
python --version
pip list | grep -E "Flask|werkzeug|PyMySQL|openpyxl"
```

### Test 3: Conectar a MySQL desde terminal local
```bash
pip install pymysql

python -c "
import pymysql

conn = pymysql.connect(
    host='tu_usuario.mysql.pythonanywhere-services.com',
    user='tu_usuario',
    password='TU_PASSWORD',
    database='tu_usuario\$teknetau_db'
)
cursor = conn.cursor()
cursor.execute('SELECT 1')
print('✓ Conexión a MySQL OK')
conn.close()
"
```

---

## LOGS Y DEBUGGING

### Ver logs de errores (PythonAnywhere)
```bash
# Error log
tail -n 50 /var/log/tu_usuario.pythonanywhere_com.error.log

# Server log
tail -n 50 /var/log/tu_usuario.pythonanywhere_com.server.log
```

### Ver logs en tiempo real
```bash
tail -f /var/log/tu_usuario.pythonanywhere_com.error.log
```

### Limpiar logs antiguos (opcional)
```bash
# En PythonAnywhere, los logs se limpian automáticamente después de 7 días
```

---

## PROBLEMAS COMUNES - SOLUCIONES RÁPIDAS

### ❌ "Access denied for user"
```bash
# Verificar credenciales
python -c "
import pymysql
conn = pymysql.connect(
    host='tu_usuario.mysql.pythonanywhere-services.com',
    user='tu_usuario',
    password='TU_PASSWORD',
    database='tu_usuario\$teknetau_db'
)
print('✓ OK')
"
```

### ❌ "No module named pymysql"
```bash
pip install --user pymysql
```

### ❌ "Lost connection to MySQL server"
Agregar en app.py (antes de return conn):
```python
conn.autocommit = True
```

### ❌ "Charset utf8mb4 not supported"
Usar en conexión:
```python
charset='utf8mb4'
```

### ❌ "Application has timed out"
En PythonAnywhere → Web → Increase Timeout to 300

---

## LIMPIAR CACHE Y REINICIAR

```bash
# Limpiar cache Python
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO"
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# En PythonAnywhere, recargar:
touch /var/www/tu_usuario_pythonanywhere_com_wsgi.py
```

---

## RESPALDO Y RECUPERACIÓN

### Hacer backup de BD MySQL
```bash
# Local (Windows)
mysqldump -h tu_usuario.mysql.pythonanywhere-services.com ^
          -u tu_usuario ^
          -p tu_usuario$teknetau_db > backup.sql

# Linux/Mac
mysqldump -h tu_usuario.mysql.pythonanywhere-services.com \
          -u tu_usuario \
          -p tu_usuario$teknetau_db > backup.sql
```

### Restaurar desde backup
```bash
mysql -h tu_usuario.mysql.pythonanywhere-services.com \
      -u tu_usuario \
      -p tu_usuario$teknetau_db < backup.sql
```

---

## VERIFICACIÓN FINAL

### Checklist antes de dar por terminado
```bash
# 1. ¿Está limpio el código?
[ ] Archivos innecesarios eliminados
[ ] Solo archivos esenciales en carpeta

# 2. ¿Funciona localmente?
python app.py  # ← Debe abrir en http://localhost:5000

# 3. ¿Se conecta a MySQL?
python -c "from app import get_db_connection; conn = get_db_connection(); print('OK')"

# 4. ¿Está en PythonAnywhere?
[ ] Código subido
[ ] requirements.txt instalado
[ ] Variables de entorno configuradas
[ ] WSGI actualizado
[ ] Tabla web reloaded

# 5. ¿Todo funciona en producción?
[ ] https://tu_usuario.pythonanywhere.com abre sin errores
[ ] Puedo hacer login
[ ] Puedo ver datos
[ ] Puedo crear nuevos registros
```

---

## CONTACTO CON SOPORTE

Si algo no funciona:

1. **Revisar logs:** `tail -f /var/log/...error.log`
2. **Probar conexión:** `python test_mysql_connection.py`
3. **Recargar app:** `touch wsgi.py`
4. **Limpiar cache:** `find . -name __pycache__ -exec rm -r {} +`

---

**¡Listo para desplegar! 🚀**

