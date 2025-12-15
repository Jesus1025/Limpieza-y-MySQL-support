#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificación - TekneTau
Verifica que todo está limpio y actualizado
"""

import os
import sys
from pathlib import Path

def check_cleanup():
    """Verificar limpieza."""
    print("\n📁 VERIFICANDO LIMPIEZA...")
    print("─" * 50)
    
    archivos_esperados = [
        'test_api.py',
        'test_api_response.py',
        'test_auth.py',
        'test_docs.py',
        'check_db.py',
        'debug_db.py',
        'crear_usuario.py',
        'INSTRUCCIONES_PYTHONANYWHERE.md',
        'RESUMEN_DEPLOYMENT.md',
        'server.log',
    ]
    
    archivos_encontrados = 0
    for archivo in archivos_esperados:
        if Path(archivo).exists():
            print(f"❌ Aún existe: {archivo}")
            archivos_encontrados += 1
    
    if archivos_encontrados == 0:
        print(f"✅ Todos los archivos innecesarios han sido eliminados")
    else:
        print(f"⚠️  Aún hay {archivos_encontrados} archivos que deberían eliminarse")
    
    return archivos_encontrados == 0


def check_mysql_support():
    """Verificar soporte MySQL."""
    print("\n🔌 VERIFICANDO SOPORTE MYSQL...")
    print("─" * 50)
    
    try:
        import pymysql
        print(f"✅ PyMySQL instalado (versión {pymysql.__version__})")
        return True
    except ImportError:
        print(f"❌ PyMySQL no instalado")
        return False


def check_app_structure():
    """Verificar estructura de archivos esenciales."""
    print("\n📋 VERIFICANDO ESTRUCTURA...")
    print("─" * 50)
    
    archivos_esenciales = [
        'app.py',
        'wsgi.py',
        'requirements.txt',
        'database/',
        'templates/',
        'static/',
        'uploads/',
    ]
    
    all_exist = True
    for archivo in archivos_esenciales:
        path = Path(archivo)
        if path.exists():
            tipo = "📁" if path.is_dir() else "📄"
            print(f"{tipo} {archivo} ✅")
        else:
            print(f"❌ Falta: {archivo}")
            all_exist = False
    
    return all_exist


def check_app_py_mysql():
    """Verificar que app.py tiene soporte MySQL."""
    print("\n🔧 VERIFICANDO CÓDIGO MYSQL EN app.py...")
    print("─" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'import pymysql': 'Import de PyMySQL',
            'get_db_connection()': 'Función de conexión dual',
            'ENVIRONMENT = os.environ': 'Detección de entorno',
            'MYSQL_AVAILABLE': 'Verificación de MySQL',
        }
        
        all_found = True
        for check, description in checks.items():
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ Falta: {description}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error al leer app.py: {e}")
        return False


def check_requirements_pymysql():
    """Verificar que requirements.txt incluye PyMySQL."""
    print("\n📦 VERIFICANDO requirements.txt...")
    print("─" * 50)
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        if 'PyMySQL' in content:
            print(f"✅ PyMySQL en requirements.txt")
            return True
        else:
            print(f"❌ PyMySQL NO está en requirements.txt")
            return False
    except Exception as e:
        print(f"❌ Error al leer requirements.txt: {e}")
        return False


def main():
    print("\n" + "=" * 50)
    print("   🚀 VERIFICACIÓN DE LIMPIEZA Y ACTUALIZACIONES")
    print("=" * 50)
    
    results = {
        '✅ Limpieza': check_cleanup(),
        '✅ MySQL instalado': check_mysql_support(),
        '✅ Estructura': check_app_structure(),
        '✅ app.py MySQL': check_app_py_mysql(),
        '✅ requirements.txt': check_requirements_pymysql(),
    }
    
    print("\n" + "=" * 50)
    print("   📊 RESUMEN FINAL")
    print("=" * 50)
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    for check, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {check}")
    
    print("\n" + "=" * 50)
    if all(results.values()):
        print(f"✅ TODOS LOS CHECKS PASARON ({passed_checks}/{total_checks})")
        print("\n🎉 ¡Tu aplicación está lista para deployment!")
        print("\nPróximos pasos:")
        print("1. Sube el código a PythonAnywhere")
        print("2. Crea una BD MySQL en PythonAnywhere")
        print("3. Configura variables de entorno en wsgi.py")
        print("4. Sigue GUIA_MYSQL_PYTHONANYWHERE.md")
        print("=" * 50)
        return 0
    else:
        print(f"⚠️  ALGUNOS CHECKS FALLARON ({passed_checks}/{total_checks})")
        print("\nVerifica los errores anteriores y corrige.")
        print("=" * 50)
        return 1


if __name__ == '__main__':
    sys.exit(main())
