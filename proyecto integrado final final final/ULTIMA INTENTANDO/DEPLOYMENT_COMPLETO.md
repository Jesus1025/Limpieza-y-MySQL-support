# 🚀 DEPLOYMENT COMPLETO: PYTHONANYWHERE + MYSQL

## ÍNDICE DE DOCUMENTOS (Lee en este orden)

1. **QUICK_REFERENCE.md** ← Resumen en 1 página (empieza aquí)
2. **GUIA_DEPLOYMENT_PASO_A_PASO.md** ← Instrucciones detalladas
3. **GUIA_VISUAL_PYTHONANYWHERE.md** ← Pantallas visuales
4. **Este archivo** ← Integración completa

---

## TU SITUACIÓN ACTUAL

✅ **Código en tu máquina:**
- app.py actualizado con soporte MySQL
- requirements.txt con PyMySQL
- Todos los templates y static files listos
- Verificación completada (5/5 checks)

⏳ **Próximo paso:**
- Subir a PythonAnywhere
- Conectar a MySQL
- ¡Ir en vivo!

---

## FLUJO GENERAL DE DEPLOYMENT

```
Tu máquina local          PythonAnywhere              BD MySQL
      │                        │                          │
      │ 1. Código listo        │                          │
      │────────────────────────→                          │
      │                        │ 2. Instalar deps         │
      │                        │───────────────→          │
      │                        │ 3. Crear tablas          │
      │                        │───────────────→          │
      │                        │ 4. Conectar              │
      │                        │                          │
      │                        ↓                          │
      │                    ✅ LIVE                        │
      │
      └──→ Usuario accede desde navegador
          ↓
          Tu app en PythonAnywhere
          ↓
          Conecta a MySQL en PythonAnywhere
          ↓
          ÉXITO 🎉
```

---

## RESUMEN: PASO A PASO (30 minutos)

### Fase 1: Preparar (5 min)
```
☐ Verificar que código está limpio: python verify.py
☐ Revisar requirements.txt tiene PyMySQL
☐ Tener a mano credenciales PythonAnywhere
```

### Fase 2: Crear BD MySQL en PythonAnywhere (2 min)
```
☐ Ir a PythonAnywhere → Databases
☐ Crear BD MySQL con nombre: tu_usuario$teknetau_db
☐ GUARDAR: Hostname, Username, Password, Database
```

### Fase 3: Subir código a PythonAnywhere (5 min)
```
☐ OPCIÓN A: git push (si tienes Git)
☐ OPCIÓN B: SFTP upload de carpeta
```

### Fase 4: Configurar wsgi.py (5 min)
```
☐ Ir a Web → Editar WSGI config file
☐ Agregar variables de entorno de MySQL
☐ Guardar archivo
```

### Fase 5: Instalar paquetes (2 min)
```
☐ Bash Console: pip install -r requirements.txt
☐ Esperar "Successfully installed"
```

### Fase 6: Crear tablas (3 min)
```
☐ Bash Console: python
☐ Ejecutar init_database()
☐ Esperar "✅ Tablas creadas"
```

### Fase 7: Recargar y probar (5 min)
```
☐ Web: Click "Reload"
☐ Esperar 10 segundos
☐ Abrir https://tu_usuario.pythonanywhere.com
☐ Probar login
☐ Crear cliente de prueba
☐ Verificar en BD
```

---

## PLANTILLA wsgi.py (COPIAR Y PEGAR)

```python
import os
import sys

# ============================================
# CONFIGURACIÓN MYSQL PARA PRODUCCIÓN
# ============================================

os.environ['ENVIRONMENT'] = 'production'
os.environ['MYSQL_HOST'] = 'tu_usuario.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'tu_usuario'
os.environ['MYSQL_PASSWORD'] = 'tu_contraseña_aqui'
os.environ['MYSQL_DATABASE'] = 'tu_usuario$teknetau_db'
os.environ['SECRET_KEY'] = 'tu_clave_segura_aqui'

# ============================================

path = '/home/tu_usuario/proyecto_integrado'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

**Valores a reemplazar:**
- `tu_usuario` → Tu usuario de PythonAnywhere
- `tu_contraseña_aqui` → Contraseña de MySQL (del paso 2)
- `tu_clave_segura_aqui` → Cualquier string aleatorio (ej: "abc123xyz")

---

## COMANDOS BASH PARA COPIAR Y PEGAR

### Comando 1: Ir a carpeta
```bash
cd /home/tu_usuario/proyecto_integrado
```

### Comando 2: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Comando 3: Verificar instalación
```bash
python -c "import pymysql; print('✅ PyMySQL instalado')"
```

### Comando 4: Crear tablas
```bash
python << 'EOF'
from app import app, init_database
with app.app_context():
    init_database()
    print("✅ Tablas creadas exitosamente")
EOF
```

### Comando 5: Probar conexión
```bash
python -c "from app import app, get_db_connection; conn = get_db_connection(); print('✅ Conectado a BD'); conn.close()"
```

---

## LISTA DE VERIFICACIÓN FINAL

### Antes de comenzar
- [ ] Tengo usuario en PythonAnywhere
- [ ] Código está en mi máquina
- [ ] verify.py pasó todos los checks
- [ ] requirements.txt tiene PyMySQL

### Durante el deployment
- [ ] BD MySQL creada en PythonAnywhere
- [ ] Credenciales guardadas
- [ ] Código subido a PythonAnywhere
- [ ] wsgi.py configurado con variables
- [ ] pip install -r requirements.txt ejecutado
- [ ] Tablas creadas (init_database corrió)
- [ ] Web app recargada

### Después de deploy
- [ ] https://tu_usuario.pythonanywhere.com funciona
- [ ] Página de login carga
- [ ] Login funciona
- [ ] Puedo crear un cliente
- [ ] Los datos aparecen en BD MySQL
- [ ] Exportar CSV funciona
- [ ] Exportar PDF funciona

Si todo está ✅ → **¡DEPLOYMENT EXITOSO!** 🎉

---

## TROUBLESHOOTING RÁPIDO

### Si ves "ModuleNotFoundError: No module named 'pymysql'"
```bash
pip install PyMySQL
# Luego reload web app
```

### Si ves "Can't connect to MySQL server"
```bash
# Verificar variables en wsgi.py son correctas
# Ir a Databases → copiar credenciales nuevamente
# Pegar en wsgi.py
# Reload web app
```

### Si ves "404 Not Found"
```bash
# Reload web app
# Esperar 30 segundos
# Intentar de nuevo
```

### Si ves "Internal Server Error (500)"
```bash
# Bash: python /var/www/tu_usuario_pythonanywhere_com_wsgi.py
# Ver el error exacto que muestra
# Usualmente error en wsgi.py (sintaxis)
```

### Si falta carpeta templates/ o static/
```bash
# Re-subir código completo
# Asegurarse que todas las carpetas se subieron
```

---

## DESPUÉS DEL DEPLOYMENT

### Próximas configuraciones (OPCIONAL)

1. **Dominio personalizado**
   - Ir a Web → Agregar dominio personalizado
   - Configurar DNS en registrador

2. **Backups de BD**
   - Crear script para backup automático
   - Guardar en carpeta uploads/

3. **Monitoreo**
   - Revisar logs regularmente
   - Configurar alertas de errores

4. **Scaling**
   - Si crece el tráfico, considerar plan premium
   - Aumentar recursos de BD

---

## SOPORTE Y DEBUGGING

### Logs disponibles en PythonAnywhere

1. **Error log** (Web → Scroll → Error log)
   - Errores de la app
   - Última opción para debugging

2. **Access log** (Web → Scroll → Access log)
   - Requests recibidos
   - Códigos de respuesta HTTP

3. **Bash console**
   - Ejecutar comandos directamente
   - Ver output en tiempo real

### Debugging steps

```bash
# Paso 1: ¿Funciona la app?
python -c "from app import app; print('OK')"

# Paso 2: ¿Funciona MySQL?
python -c "import pymysql; print('OK')"

# Paso 3: ¿Se conecta a BD?
python << 'EOF'
from app import get_db_connection
try:
    conn = get_db_connection()
    print("✅ Conectado")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
EOF

# Paso 4: ¿Las tablas existen?
mysql -h HOST -u USER -p
mysql> SHOW TABLES;
mysql> exit
```

---

## CHECKLIST FINAL

```
DEPLOYMENT A PYTHONANYWHERE + MYSQL

Antes de comenzar:
  ☐ verify.py pasó todos los checks
  ☐ requirements.txt tiene PyMySQL
  ☐ Tengo credenciales PythonAnywhere

Crear BD:
  ☐ BD MySQL creada
  ☐ Credenciales guardadas

Subir código:
  ☐ Código en PythonAnywhere
  ☐ Todas las carpetas presentes

Configurar:
  ☐ wsgi.py con variables
  ☐ pip install ejecutado
  ☐ Tablas creadas

Probar:
  ☐ Login funciona
  ☐ Crear cliente funciona
  ☐ Data en MySQL
  ☐ CSV export funciona
  ☐ PDF export funciona

Resultado:
  ☐ ✅ APLICACIÓN EN VIVO

Tiempo total: ~30-40 minutos
Dificultad: BAJA (todo está documentado)
```

---

## PREGUNTAS FRECUENTES

**P: ¿Cuánto cuesta PythonAnywhere?**
R: Tiene plan gratuito limitado. Para producción, ~$5-15/mes.

**P: ¿Se puede usar dominio personalizado?**
R: Sí, en planes pagos. En gratuito es subdomain.pythonanywhere.com

**P: ¿Cuáles son los límites de base de datos?**
R: Plan gratuito: 20 MB. Plan pro: 1 GB+. Para producción es suficiente.

**P: ¿Si falla MySQL, qué pasa?**
R: Fallback automático a SQLite local. La app NO se cae.

**P: ¿Puedo cambiar la BD de SQLite a MySQL después?**
R: Sí, pero tendrías que migrar datos. Mejor hacerlo desde el inicio.

**P: ¿Cómo hago backup de la BD?**
R: Bash: `mysqldump -h HOST -u USER -p DB > backup.sql`

**P: ¿Se puede hacer CI/CD (auto-deploy)?**
R: Sí, conectando Git. Cada push hace deploy automático.

---

## RECURSOS EXTERNOS

- **PythonAnywhere Docs:** https://help.pythonanywhere.com/
- **Flask Docs:** https://flask.palletsprojects.com/
- **MySQL Docs:** https://dev.mysql.com/doc/
- **PyMySQL Docs:** https://pymysql.readthedocs.io/

---

## SIGUIENTE PASO

1. **Lee:** QUICK_REFERENCE.md (1 página)
2. **Sigue:** GUIA_DEPLOYMENT_PASO_A_PASO.md (paso a paso)
3. **Consulta:** GUIA_VISUAL_PYTHONANYWHERE.md (si tienes dudas)
4. **Prueba:** En PythonAnywhere
5. **Éxito:** ¡Tu app en vivo! 🎉

---

**¡Adelante con el deployment!** 🚀

Última actualización: 15 de Diciembre de 2025
Estado: ✅ Listo para deployment
Tiempo estimado: 30-40 minutos
Dificultad: BAJA

