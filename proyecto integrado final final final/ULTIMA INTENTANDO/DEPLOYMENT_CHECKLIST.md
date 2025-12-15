# 🎯 CHECKLIST DE DEPLOYMENT A PYTHONANYWHERE

## ✅ FASE 1: PREPARACIÓN LOCAL (COMPLETADA)

- [x] Limpiar proyecto (eliminar 11 archivos innecesarios)
- [x] Actualizar app.py con soporte MySQL
- [x] Instalar PyMySQL localmente
- [x] Actualizar requirements.txt
- [x] Verificar estructura y código
- [x] Documentar cambios

**Estado:** ✅ COMPLETADO

---

## 📋 FASE 2: SETUP EN PYTHONANYWHERE (PRÓXIMA)

### 2.1 Crear Base de Datos MySQL

- [ ] Ir a PythonAnywhere Dashboard
- [ ] Click en "Databases" 
- [ ] Click en "Add new database"
- [ ] Seleccionar "MySQL"
- [ ] Nombre: `tu_usuario$teknetau_db`
- [ ] Generar contraseña (guardar)
- [ ] Click en "Create"

**Tiempo estimado:** 2 minutos

### 2.2 Subir Código

Opción A - Git:
- [ ] `git push` (si usas Git)

Opción B - SFTP Manual:
- [ ] Conectar SFTP a PythonAnywhere
- [ ] Subir carpeta `proyecto integrado/`
- [ ] Mantener estructura igual

**Tiempo estimado:** 5 minutos

### 2.3 Configurar Variables de Entorno

En PythonAnywhere, editar `/var/www/tu_usuario_pythonanywhere_com_wsgi.py`:

```python
import os

os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'CONTRASEÑA_GENERADA_EN_PASO_2.1'
os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'
os.environ['SECRET_KEY'] = 'GENERAR_UNA_CLAVE_SEGURA_MUY_LARGA_AQUI'

# Resto del código wsgi.py...
from app import app as application
```

**Instrucciones:**
1. Ir a "Web" en PythonAnywhere
2. Click en archivo `tu_usuario_pythonanywhere_com_wsgi.py`
3. Editar como se muestra arriba
4. Guardar

**Tiempo estimado:** 5 minutos

### 2.4 Instalar Dependencias

En PythonAnywhere Bash Console:

```bash
cd /home/tu_usuario/proyecto_integrado
pip install -r requirements.txt
```

**Tiempo estimado:** 2 minutos

### 2.5 Crear Tablas MySQL (Migrations)

En PythonAnywhere Bash Console:

```bash
cd /home/tu_usuario/proyecto_integrado
python
```

Luego en Python console:

```python
from app import app, init_database

with app.app_context():
    init_database()
    print("✅ Tablas creadas en MySQL")
    exit()
```

**Tiempo estimado:** 3 minutos

---

## 🧪 FASE 3: VERIFICACIÓN (PRÓXIMA)

### 3.1 Recargar Aplicación Web

En PythonAnywhere Dashboard:
- [ ] Ir a "Web"
- [ ] Click botón "Reload"
- [ ] Esperar 10 segundos

### 3.2 Prueba Básica

- [ ] Abrir: `https://tu_usuario.pythonanywhere.com`
- [ ] Verificar que carga la página de login
- [ ] No debe mostrar errores en la consola

### 3.3 Prueba de Login

- [ ] Probar login con usuario/contraseña
- [ ] Verificar que entra al dashboard
- [ ] Comprobar que se puede navegar

### 3.4 Prueba de Base de Datos

- [ ] En "Clientes": crear un cliente nuevo
- [ ] Verificar que aparece en la lista
- [ ] Esto confirma que MySQL funciona ✓

### 3.5 Prueba de Exportación

- [ ] Ir a "Reportes"
- [ ] Exportar a CSV
- [ ] Descargar y abrir archivo
- [ ] Verificar que datos están correctos

**Tiempo estimado:** 5 minutos

---

## 🐛 FASE 4: DEBUGGING (SI ALGO FALLA)

### Error: "ModuleNotFoundError: No module named 'pymysql'"

**Solución:**
```bash
# En PythonAnywhere Bash:
pip install PyMySQL
```

### Error: "Can't connect to MySQL server"

**Checklist:**
- [ ] Variables de entorno correctas en wsgi.py
- [ ] Database creada en PythonAnywhere
- [ ] Contraseña correcta
- [ ] Ir a "Databases" en PythonAnywhere y verificar

### Error: "ERRCODE_UNKNOWN_ERROR"

**Solución:**
- [ ] Recargar web app desde PythonAnywhere
- [ ] Esperar 30 segundos
- [ ] Intentar de nuevo

### Ver Logs de Error

En PythonAnywhere:
1. Ir a "Web"
2. Scroll hasta abajo
3. Ver "Error log" y "Server log"
4. Buscar mensajes de error rojos

---

## 📊 RESUMEN DE DEPLOYMENT

| Fase | Tarea | Tiempo | Estado |
|------|-------|--------|--------|
| 1 | Preparación local | 15 min | ✅ HECHO |
| 2 | Setup PythonAnywhere | 20 min | ⏳ PRÓXIMO |
| 3 | Verificación | 5 min | ⏳ PRÓXIMO |
| 4 | Debugging | Según sea | ⏳ PRÓXIMO |
| **TOTAL** | **Deployment** | **~40 min** | - |

---

## 🔗 REFERENCIAS RÁPIDAS

### Documentación Completa
- 📄 `GUIA_MYSQL_PYTHONANYWHERE.md` - Guía detallada
- 📄 `COMANDOS_RAPIDOS.md` - Comandos copy-paste
- 📄 `STATUS_FINAL.md` - Este status

### Archivos Importantes
- 📄 `app.py` - Aplicación principal (ACTUALIZADO)
- 📄 `wsgi.py` - Configuración PythonAnywhere
- 📄 `requirements.txt` - Dependencias (ACTUALIZADO)
- 📄 `verify.py` - Script de verificación

### URLs Útiles
- 🔗 Dashboard local: `http://localhost:5000`
- 🔗 Dashboard PythonAnywhere: `https://tu_usuario.pythonanywhere.com`
- 🔗 PythonAnywhere Dashboard: `https://www.pythonanywhere.com/user/tu_usuario/`

---

## ⚡ QUICK START

**Para deployment rápido, sigue estos 5 pasos:**

```
1. Crear BD MySQL en PythonAnywhere ✓
   └─ Tiempo: 2 min

2. Configurar wsgi.py con variables ✓
   └─ Tiempo: 5 min

3. Instalar dependencias ✓
   └─ Tiempo: 2 min

4. Crear tablas (init_database) ✓
   └─ Tiempo: 3 min

5. Recargar y probar ✓
   └─ Tiempo: 5 min

TOTAL: 17 MINUTOS ⚡
```

---

## 🎉 RESULTADO FINAL

✅ **Tu aplicación TekneTau**
- Limpia y optimizada
- Con soporte MySQL
- Lista para producción
- Deployment ready

**Ahora:** Sigue `GUIA_MYSQL_PYTHONANYWHERE.md` paso a paso

---

**Última actualización:** 15 de Diciembre de 2025
**Tiempo estimado de deployment:** 40-60 minutos
**Dificultad:** Baja (todo está documentado)

