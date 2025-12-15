# TEKNETAU - Sistema de Gestión de Facturación

Aplicación web para la gestión de clientes, facturas, boletas, notas de crédito y reportes.

## Instalación en PythonAnywhere

1. **Clonar repositorio**
```bash
git clone https://github.com/Jesus1025/Limpieza-y-MySQL-support.git
cd "proyecto integrado"
```

2. **Crear tabla MySQL** (ejecutar una sola vez)
```bash
python create_mysql_tables.py
```

3. **Recargar la web app**
En el dashboard de PythonAnywhere → Web → Click Reload

## Credenciales por defecto

**Usuario:** admin  
**Contraseña:** admin123

## Requisitos

- Python 3.9+
- MySQL (en PythonAnywhere)
- Paquetes en requirements.txt

## Estructura

- `app.py` - Aplicación Flask principal
- `wsgi.py` - Punto de entrada para PythonAnywhere
- `config.py` - Configuración (no modificar)
- `templates/` - Plantillas HTML
- `static/` - CSS, JavaScript
- `database/` - BD SQLite (desarrollo local)

## Notas de Producción

- ✅ MySQL está forzado en PythonAnywhere
- ✅ Sesiones seguras (HTTPS requerido)
- ✅ Las tablas se crean automáticamente en MySQL
- ✅ El archivo `create_mysql_tables.py` solo necesita ejecutarse una vez

---

**Versión:** 2.0 (Limpia para Producción)  
**Última actualización:** Diciembre 2025
