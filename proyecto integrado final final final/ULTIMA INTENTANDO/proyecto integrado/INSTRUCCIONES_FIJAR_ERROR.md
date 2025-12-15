# 🔧 INSTRUCCIONES PARA FIJAR EL ERROR EN PYTHONANYWHERE

## ✅ PASO 1: Asegúrate que el código esté actualizado en PythonAnywhere

En **Bash Console de PythonAnywhere**:

```bash
cd ~/proyecto_integrado/proyecto\ integrado\ final\ final\ final/ULTIMA\ INTENTANDO/proyecto\ integrado
git pull origin main
```

## ✅ PASO 2: Crea las tablas MySQL necesarias

Ejecuta el script que crearemos:

```bash
python create_mysql_tables.py
```

Debería mostrar:
```
✅ TODAS LAS TABLAS CREADAS EXITOSAMENTE
📊 Tablas en la BD:
   - clientes
   - usuarios
   - documentos
```

## ✅ PASO 3: Recarga la web app en PythonAnywhere

En el **Dashboard de PythonAnywhere**:
1. Ve a la sección **"Web"**
2. Click en tu aplicación `Teknetautest.pythonanywhere.com`
3. Click en el botón **"Reload"** (arriba)

Espera 30 segundos.

## ✅ PASO 4: Verifica el status de la BD

Abre en el navegador:

```
https://Teknetautest.pythonanywhere.com/api/debug/status
```

Deberías ver:
```json
{
  "status": "OK",
  "database": "MySQL",
  "use_mysql": true,
  "tables": ["clientes", "usuarios", "documentos"],
  "timestamp": "2025-12-15T22:30:00..."
}
```

Si ves error, significa que MySQL no está conectando. Revisa en **Web** → **Log files**.

## ✅ PASO 5: Intenta crear un cliente

Abre:
```
https://Teknetautest.pythonanywhere.com/clientes
```

Y haz clic en **"+ Nuevo Cliente"**.

## ⚠️ SI AÚN HAY ERROR

En Bash Console:

```bash
python app.py
```

Y observa qué error aparece. Si dice algo de "usuarios table", significa que aún falta crear esa tabla.

---

## 📊 Resumen de cambios en el código

1. **init_database()** - Ahora es SEGURO para MySQL y SQLite
   - Solo se ejecuta en desarrollo local, NO en PythonAnywhere
   - Crea tablas: clientes, usuarios, documentos
   - Usa `IF NOT EXISTS` para evitar errores

2. **get_db_connection()** - Fuerza MySQL
   - Lanza error claro si MySQL no conecta
   - Fallback a SQLite solo en desarrollo

3. **Nuevo endpoint `/api/debug/status`** - Para debugging
   - Muestra qué BD está usando
   - Lista todas las tablas creadas
   - Útil para troubleshooting

---

## 🎯 PRÓXIMA PRUEBA DESPUÉS DE ESTOS PASOS

1. Abre `/api/debug/status` → Verifica que muestre MySQL
2. Abre `/clientes` → Intenta crear cliente nuevo
3. Verifica en MySQL que se guardó el cliente

Si todo funciona, ¡listo! 🚀
