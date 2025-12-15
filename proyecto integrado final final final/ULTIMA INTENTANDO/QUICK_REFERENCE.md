# ⚡ REFERENCIA RÁPIDA: DEPLOYMENT A PYTHONANYWHERE

## 6 PASOS EN 30 MINUTOS

### PASO 1: CREAR BD MYSQL (2 min)
```
URL: https://www.pythonanywhere.com/user/tu_usuario/
Click: Databases
Click: Add new database → MySQL
Nombre: tu_usuario$teknetau_db
Guardar: Hostname, User, Pass, Database
```

### PASO 2: SUBIR CÓDIGO (5 min)
```
OPCIÓN A - Git:
$ git push

OPCIÓN B - SFTP:
Upload carpeta proyecto_integrado/ a /home/tu_usuario/
```

### PASO 3: CONFIGURAR wsgi.py (5 min)
```
URL: https://www.pythonanywhere.com/user/tu_usuario/
Click: Web
Click: tu_usuario.pythonanywhere.com
Buscar: WSGI configuration file
Click: /var/www/tu_usuario_pythonanywhere_com_wsgi.py

Editar y agregar al INICIO del archivo:

import os

os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'tu_contraseña_de_mysql'
os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'
os.environ['SECRET_KEY'] = 'una_clave_segura_aqui'

Click: Save
```

### PASO 4: INSTALAR DEPENDENCIAS (2 min)
```
URL: https://www.pythonanywhere.com/user/tu_usuario/
Click: Consoles
Click: Start new Bash console

$ cd /home/tu_usuario/proyecto_integrado
$ pip install -r requirements.txt

Esperar hasta: "Successfully installed..."
```

### PASO 5: CREAR TABLAS MYSQL (3 min)
```
En la misma Bash Console:

$ python

>>> from app import app, init_database
>>> with app.app_context():
...     init_database()
...     exit()

Deberías ver: ✅ Tablas creadas
```

### PASO 6: RECARGAR Y PROBAR (5 min)
```
URL: https://www.pythonanywhere.com/user/tu_usuario/
Click: Web
Click: [Reload tu_usuario.pythonanywhere.com]

Esperar 10 segundos.

Abrir: https://tu_usuario.pythonanywhere.com
Login con usuario/contraseña
¡Crear cliente de prueba!
```

---

## DATOS A GUARDAR

```
De PythonAnywhere Databases:
Hostname: ________________________
Username: ________________________
Password: ________________________
Database: ________________________

De tu máquina local:
Usuario app: ________________________
Contraseña: ________________________
```

---

## ERRORES: SOLUCIONES RÁPIDAS

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: pymysql` | `pip install PyMySQL` en Bash |
| `Can't connect to MySQL` | Verifica variables en wsgi.py |
| `404 Not Found` | Reload web app, esperar 30 seg |
| `Internal Server Error (500)` | Ver Error log en Web |
| `FileNotFoundError: templates/...` | Re-subir código (carpeta incompleta) |

---

## VERIFICACIÓN

```bash
# Para verificar que todo está bien en Bash Console:

cd /home/tu_usuario/proyecto_integrado

# Test 1: ¿Funciona la app?
python -c "from app import app; print('✅ app.py OK')"

# Test 2: ¿Funciona MySQL?
python -c "import pymysql; print('✅ PyMySQL OK')"

# Test 3: ¿Conecta a BD?
python << 'EOF'
from app import app, get_db_connection
with app.app_context():
    try:
        conn = get_db_connection()
        print("✅ Conexión a BD OK")
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")
EOF
```

---

## URLS IMPORTANTES

```
Dashboard: https://www.pythonanywhere.com/user/tu_usuario/
Tu App:    https://tu_usuario.pythonanywhere.com
Databases: https://www.pythonanywhere.com/user/tu_usuario/mysql/
Web Apps:  https://www.pythonanywhere.com/user/tu_usuario/webapps/
Consoles:  https://www.pythonanywhere.com/user/tu_usuario/consoles/
```

---

## ARCHIVOS IMPORTANTES

```
Local (tu máquina):
  app.py                    ← Código principal
  requirements.txt          ← Dependencias
  wsgi.py                   ← Config PythonAnywhere

PythonAnywhere:
  /home/tu_usuario/proyecto_integrado/app.py
  /var/www/tu_usuario_pythonanywhere_com_wsgi.py
```

---

## CHEATSHEET BASH CONSOLE

```bash
# Navegar
cd /home/tu_usuario/proyecto_integrado
pwd                    # Ver dónde estoy
ls -la                 # Listar archivos

# Instalar
pip install -r requirements.txt
pip install PyMySQL   # Si falta

# Probar conexión
mysql -h HOST -u USER -p    # Pide contraseña
# Si entra → conexión OK
# exit para salir

# Python console
python

# Test rápido
python -c "from app import app; print('OK')"
```

---

## SI TODO FUNCIONA ✅

```
✅ Página de login accesible
✅ Login funciona
✅ Puedo crear clientes
✅ Los datos se guardan en MySQL
✅ Puedo descargar CSV
✅ Puedo descargar PDF

= ¡DEPLOYMENT COMPLETADO! 🎉
```

---

## PRÓXIMOS PASOS (DESPUÉS DE LIVE)

1. Configurar dominio personalizado (opcional)
2. Configurar SSL/HTTPS (PythonAnywhere lo hace auto)
3. Backup automático de BD (si es importante)
4. Monitoreo y logs
5. Scaling si crece el tráfico

---

**¡Tu aplicación está en producción!** 🚀

