# 🚀 GUÍA COMPLETA: SUBIR A PYTHONANYWHERE Y CONECTAR MYSQL

## PARTE 1: PREPARAR CÓDIGO LOCALMENTE (5 minutos)

### Paso 1.1: Verificar que todo está listo
```bash
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO\proyecto integrado"
python verify.py
```

Deberías ver: ✅ TODOS LOS CHECKS PASARON (5/5)

### Paso 1.2: Asegurar que requirements.txt está correcto
```bash
cat requirements.txt
```

Debe contener:
```
flask>=2.0.0
werkzeug>=2.0.0
openpyxl>=3.0.0
PyMySQL>=1.0.2
```

✅ Si está bien, procede al siguiente paso.

---

## PARTE 2: CREAR BASE DE DATOS EN PYTHONANYWHERE (10 minutos)

### Paso 2.1: Ir a PythonAnywhere Dashboard

1. Abre: https://www.pythonanywhere.com
2. Login con tu usuario
3. Click en "Dashboard"

### Paso 2.2: Crear Base de Datos MySQL

1. Click en "Databases" (en menú superior)
2. Click en botón azul "Add a new database"
3. Seleccionar: "MySQL"
4. Nombre de BD: `tu_usuario$teknetau_db`
   - Cambia `tu_usuario` por tu usuario de PythonAnywhere
   - Ejemplo: Si tu usuario es "jesus123", sería: `jesus123$teknetau_db`
5. Generar contraseña (auto-generada)
6. Click en "Create MySQL database"

### Paso 2.3: Guardar datos de conexión

Verás algo como:
```
Connection settings:
Hostname: tu_usuario.mysql.pythonanywhere-services.com
Username: tu_usuario
Database: tu_usuario$teknetau_db
Password: xxxxxxxxxxxxx
```

**IMPORTANTE: Guarda estos datos en un lugar seguro** (bloc de notas temporal)
- Hostname
- Username
- Password
- Database name

---

## PARTE 3: SUBIR CÓDIGO A PYTHONANYWHERE (10 minutos)

### Opción A: VIA GIT (Recomendado - más rápido)

Si tienes Git configurado:

#### Paso 3A.1: Hacer commit local
```bash
cd "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO\proyecto integrado"
git status
git add .
git commit -m "Limpieza y MySQL support"
git push
```

#### Paso 3A.2: Actualizar código en PythonAnywhere
En PythonAnywhere Bash Console:
```bash
cd /home/tu_usuario/proyecto_integrado
git pull
```

### Opción B: VIA SFTP (Si no tienes Git)

#### Paso 3B.1: Conectar SFTP en VS Code
1. Instalar extensión: "SFTP" por Natizyskunk
2. Crear archivo `.sftp-config.json` en la carpeta del proyecto:

```json
{
    "name": "PythonAnywhere SFTP",
    "host": "tu_usuario.pythonanywhere.com",
    "protocol": "sftp",
    "port": 22,
    "username": "tu_usuario",
    "password": "tu_contraseña_pythonanywhere",
    "remotePath": "/home/tu_usuario/proyecto_integrado",
    "uploadOnSave": true,
    "watcher": {
        "files": "**/*",
        "autoUpload": true,
        "autoDelete": true
    }
}
```

3. Right click carpeta → Upload Folder

#### Paso 3B.2: O manualmente con SCP
```bash
# Desde tu máquina local:
scp -r "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO\proyecto integrado\*" tu_usuario@tu_usuario.pythonanywhere.com:/home/tu_usuario/proyecto_integrado/
```

---

## PARTE 4: CONFIGURAR VARIABLES DE ENTORNO (10 minutos)

### Paso 4.1: Ir a PythonAnywhere Web

1. Click en "Web" (en menú superior)
2. Click en tu sitio (debería estar ahí si creaste uno antes)
3. Scroll hasta "WSGI configuration file"
4. Click en el enlace (ej: `/var/www/tu_usuario_pythonanywhere_com_wsgi.py`)

### Paso 4.2: Editar wsgi.py

El archivo se abrirá en editor online. Al inicio, agrega esto:

```python
# =============================================
# CONFIGURACIÓN PARA MYSQL EN PRODUCCIÓN
# =============================================
import os

# Variables de entorno para MySQL
os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'CONTRASEÑA_QUE_GUARDASTE_EN_PASO_2.3'
os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'

# Generar una clave segura (copiar un UUID generado)
os.environ['SECRET_KEY'] = 'tu_uuid_o_clave_segura_aqui'

# Resto del archivo abajo...
```

**Ejemplo real:**
```python
import os

os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'jesus123.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'jesus123'
os.environ['MYSQL_PASSWORD'] = 'abc123xyz789!@#'
os.environ['MYSQL_DATABASE'] = 'jesus123$teknetau_db'
os.environ['SECRET_KEY'] = 'some-random-string-here-12345'

# El resto del archivo ya está aquí:
# from app import app as application
```

Haz click en "Save" (arriba a la derecha)

---

## PARTE 5: INSTALAR DEPENDENCIAS (5 minutos)

### Paso 5.1: Abrir Bash Console en PythonAnywhere

1. Click en "Consoles" (en menú superior)
2. Click en "Bash console" (green button)

### Paso 5.2: Instalar paquetes

```bash
# Navegar a la carpeta
cd /home/tu_usuario/proyecto_integrado

# Instalar requirements
pip install -r requirements.txt
```

Deberías ver:
```
Successfully installed Flask-2.0.0 werkzeug-2.0.0 openpyxl-3.0.0 PyMySQL-1.0.2
```

---

## PARTE 6: CREAR TABLAS EN MYSQL (5 minutos)

### Paso 6.1: En la misma Bash Console

```bash
cd /home/tu_usuario/proyecto_integrado
python
```

### Paso 6.2: Ejecutar init_database

Dentro de Python console:
```python
from app import app, init_database

with app.app_context():
    init_database()
    print("✅ Tablas creadas exitosamente")
    exit()
```

Deberías ver: `✅ Tablas creadas exitosamente`

Si ves error de conexión MySQL, verifica:
1. Variables en wsgi.py están correctas
2. Base de datos fue creada en paso 2
3. Credenciales coinciden

---

## PARTE 7: RECARGAR APLICACIÓN WEB (2 minutos)

### Paso 7.1: Recargar desde PythonAnywhere

1. Click en "Web" (menú superior)
2. Click en tu sitio
3. Scroll hasta arriba
4. Click en botón azul "Reload tu_usuario.pythonanywhere.com"
5. Esperar 10 segundos

---

## PARTE 8: VERIFICAR QUE FUNCIONA (5 minutos)

### Paso 8.1: Abrir tu aplicación

Abre en navegador: `https://tu_usuario.pythonanywhere.com`

Deberías ver la página de LOGIN

### Paso 8.2: Probar Login

1. Usuario: admin (o el que creaste)
2. Contraseña: la que configuraste
3. Click en Login

### Paso 8.3: Crear un cliente de prueba

1. Ir a "Clientes"
2. Click en "Nuevo Cliente"
3. Llenar datos (RUT, nombre, etc.)
4. Guardar

**Si aparece en la lista → ¡MYSQL FUNCIONA!** ✅

### Paso 8.4: Probar CSV Export

1. Ir a "Reportes"
2. Exportar a CSV
3. Descargar y abrir

Si abre correctamente → **¡TODO FUNCIONA!** 🎉

---

## PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: "ModuleNotFoundError: No module named 'pymysql'"

**Solución:**
```bash
# En PythonAnywhere Bash:
pip install PyMySQL
```

### Problema 2: "Can't connect to MySQL server"

**Verificar:**
1. ¿Creaste la BD en PythonAnywhere? (Paso 2)
2. ¿Las variables en wsgi.py son correctas? (Paso 4)
3. ¿El hostname es correcto? (Debe ser: `tu_usuario.mysql.pythonanywhere-services.com`)
4. ¿La contraseña tiene caracteres especiales? (Cópiala exacta)

**Solución rápida:**
```bash
# En PythonAnywhere Bash:
mysql -h tu_usuario.mysql.pythonanywhere-services.com -u tu_usuario -p

# Te pedirá contraseña. Si entra → conexión OK
# Exit con: exit
```

### Problema 3: "404 Not Found"

**Solución:**
1. ¿Recargaste la web app en Paso 7?
2. ¿Esperaste 10 segundos después de reload?
3. Si aún no funciona:
   - Click "Reload" nuevamente
   - Esperar 30 segundos
   - Intentar de nuevo

### Problema 4: "Internal Server Error (500)"

**Ver logs:**
1. Click en "Web"
2. Scroll hasta "Error log"
3. Ver últimas líneas (el error está ahí)

**Causas comunes:**
- wsgi.py tiene errores de sintaxis
- Variables de entorno mal configuradas
- Falta permisos en carpeta
- Base de datos no creada

**Solución:**
```bash
# En Bash:
python /var/www/tu_usuario_pythonanywhere_com_wsgi.py
```

Si hay error, te lo mostrará directamente.

### Problema 5: "FileNotFoundError: templates/index.html"

**Solución:**
1. Verificar que carpeta `templates/` se subió completa
2. Que contenga `index.html`
3. Si no, re-subir código (Paso 3)

---

## VERIFICACIÓN FINAL

### Checklist de Deployment:

- [ ] Base de datos MySQL creada en PythonAnywhere
- [ ] Datos de conexión guardados
- [ ] Código subido a PythonAnywhere (git o SFTP)
- [ ] wsgi.py configurado con variables de entorno
- [ ] requirements.txt instalado (pip install)
- [ ] Tablas creadas (init_database ejecutado)
- [ ] Web app recargada
- [ ] Página de login accesible
- [ ] Login funciona
- [ ] Puedo crear un cliente
- [ ] CSV export funciona

Si todo está ✅ → **¡DEPLOYMENT COMPLETADO!** 🎉

---

## RESUMEN RÁPIDO (Para hoy)

```
1. Crear BD MySQL en PythonAnywhere (2 min)
   └─ Apunta: hostname, user, password, database

2. Subir código (via Git o SFTP) (5 min)

3. Configurar wsgi.py con variables (5 min)

4. Instalar dependencias (pip install) (2 min)

5. Crear tablas (python init_database) (2 min)

6. Recargar web app (1 min)

7. Probar en navegador (5 min)

TOTAL: ~22 minutos ⚡
```

---

## SOPORTE 24/7

Si algo no funciona:

1. **Primero:** Revisa "PROBLEMAS COMUNES" arriba
2. **Segundo:** Ejecuta en Bash:
   ```bash
   python /var/www/tu_usuario_pythonanywhere_com_wsgi.py
   ```
3. **Tercero:** Revisa Error log en Web
4. **Cuarto:** Pregunta (estaré atento)

---

**¡Éxito con tu deployment!** 🚀

