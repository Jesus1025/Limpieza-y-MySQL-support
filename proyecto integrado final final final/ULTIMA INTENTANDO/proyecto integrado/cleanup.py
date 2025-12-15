#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Limpieza Automática - TekneTau
Elimina archivos innecesarios para optimizar el proyecto
"""

import os
import shutil
from pathlib import Path

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Archivos a eliminar
ARCHIVOS_ELIMINAR = [
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

# Carpetas a eliminar
CARPETAS_ELIMINAR = [
    '__pycache__',
]

def main():
    print(f"\n{BLUE}╔════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║      SCRIPT DE LIMPIEZA - TekneTau     ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════╝{RESET}\n")
    
    directorio_actual = Path.cwd()
    print(f"{YELLOW}📁 Directorio: {directorio_actual}{RESET}\n")
    
    # Confirmación
    print(f"{RED}⚠️  ADVERTENCIA:{RESET}")
    print(f"Se van a eliminar los siguientes archivos:\n")
    
    for archivo in ARCHIVOS_ELIMINAR:
        ruta = directorio_actual / archivo
        if ruta.exists():
            print(f"   ❌ {archivo}")
    
    print(f"\nY las siguientes carpetas:\n")
    for carpeta in CARPETAS_ELIMINAR:
        ruta = directorio_actual / carpeta
        if ruta.exists():
            print(f"   ❌ {carpeta}/")
    
    respuesta = input(f"\n{YELLOW}¿Estás seguro de continuar? (s/n): {RESET}")
    
    if respuesta.lower() != 's':
        print(f"\n{RED}Limpieza cancelada.{RESET}\n")
        return
    
    print(f"\n{BLUE}Iniciando limpieza...{RESET}\n")
    
    archivos_eliminados = 0
    carpetas_eliminadas = 0
    errores = 0
    
    # Eliminar archivos
    for archivo in ARCHIVOS_ELIMINAR:
        ruta = directorio_actual / archivo
        if ruta.exists():
            try:
                ruta.unlink()
                print(f"{GREEN}✓ Eliminado: {archivo}{RESET}")
                archivos_eliminados += 1
            except Exception as e:
                print(f"{RED}✗ Error al eliminar {archivo}: {e}{RESET}")
                errores += 1
    
    # Eliminar carpetas
    for carpeta in CARPETAS_ELIMINAR:
        ruta = directorio_actual / carpeta
        if ruta.exists():
            try:
                shutil.rmtree(ruta)
                print(f"{GREEN}✓ Eliminada: {carpeta}/{RESET}")
                carpetas_eliminadas += 1
            except Exception as e:
                print(f"{RED}✗ Error al eliminar {carpeta}: {e}{RESET}")
                errores += 1
    
    # Resumen
    print(f"\n{BLUE}╔════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║           RESUMEN DE LIMPIEZA          ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════╝{RESET}\n")
    
    print(f"Archivos eliminados: {GREEN}{archivos_eliminados}{RESET}")
    print(f"Carpetas eliminadas: {GREEN}{carpetas_eliminadas}{RESET}")
    if errores > 0:
        print(f"Errores: {RED}{errores}{RESET}")
    
    total_eliminado = archivos_eliminados + carpetas_eliminadas
    print(f"\n{GREEN}✓ Total eliminado: {total_eliminado} items{RESET}\n")
    
    if errores == 0:
        print(f"{GREEN}¡Limpieza completada exitosamente!{RESET}\n")
    else:
        print(f"{RED}Limpieza completada con {errores} errores.{RESET}\n")

if __name__ == '__main__':
    main()
