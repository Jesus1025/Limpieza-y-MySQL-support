#!/usr/bin/env python3
# cleanup.py - Script para limpiar archivos innecesarios

import os
import shutil
from pathlib import Path

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivos a eliminar
FILES_TO_DELETE = [
    'proyecto integrado/test_api.py',
    'proyecto integrado/test_api_response.py',
    'proyecto integrado/test_auth.py',
    'proyecto integrado/test_docs.py',
    'proyecto integrado/check_db.py',
    'proyecto integrado/debug_db.py',
    'proyecto integrado/crear_usuario.py',
    'proyecto integrado/INSTRUCCIONES_PYTHONANYWHERE.md',
    'proyecto integrado/RESUMEN_DEPLOYMENT.md',
    'proyecto integrado/server.log',
]

# Carpetas a eliminar
FOLDERS_TO_DELETE = [
    'proyecto integrado/__pycache__',
    'tmp',
    '.todo',
]

def delete_file(filepath):
    """Elimina un archivo con confirmación"""
    full_path = os.path.join(PROJECT_DIR, filepath)
    
    if not os.path.exists(full_path):
        return False
    
    try:
        os.remove(full_path)
        print(f"{GREEN}✓ Eliminado:{RESET} {filepath}")
        return True
    except Exception as e:
        print(f"{RED}✗ Error eliminando {filepath}: {e}{RESET}")
        return False

def delete_folder(folderpath):
    """Elimina una carpeta recursivamente con confirmación"""
    full_path = os.path.join(PROJECT_DIR, folderpath)
    
    if not os.path.exists(full_path):
        return False
    
    try:
        shutil.rmtree(full_path)
        print(f"{GREEN}✓ Eliminada carpeta:{RESET} {folderpath}")
        return True
    except Exception as e:
        print(f"{RED}✗ Error eliminando {folderpath}: {e}{RESET}")
        return False

def main():
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Limpieza de archivos innecesarios - TekneTau{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}\n")
    
    # Mostrar archivos a eliminar
    print(f"{YELLOW}Archivos a eliminar:{RESET}")
    for file in FILES_TO_DELETE:
        full_path = os.path.join(PROJECT_DIR, file)
        exists = "✓" if os.path.exists(full_path) else "✗"
        status = "Encontrado" if os.path.exists(full_path) else "No existe"
        print(f"  {exists} {file} ({status})")
    
    print(f"\n{YELLOW}Carpetas a eliminar:{RESET}")
    for folder in FOLDERS_TO_DELETE:
        full_path = os.path.join(PROJECT_DIR, folder)
        exists = "✓" if os.path.exists(full_path) else "✗"
        status = "Encontrada" if os.path.exists(full_path) else "No existe"
        print(f"  {exists} {folder} ({status})")
    
    # Pedir confirmación
    print(f"\n{YELLOW}{'='*60}{RESET}")
    response = input(f"{YELLOW}¿Deseas proceder con la eliminación? (s/n): {RESET}").lower().strip()
    
    if response != 's' and response != 'y':
        print(f"{RED}Operación cancelada.{RESET}\n")
        return
    
    # Eliminar archivos
    print(f"\n{YELLOW}Eliminando archivos...{RESET}")
    deleted_files = sum(1 for f in FILES_TO_DELETE if delete_file(f))
    
    # Eliminar carpetas
    print(f"\n{YELLOW}Eliminando carpetas...{RESET}")
    deleted_folders = sum(1 for f in FOLDERS_TO_DELETE if delete_folder(f))
    
    # Resumen
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{GREEN}✓ Limpieza completada!{RESET}")
    print(f"  Archivos eliminados: {deleted_files}")
    print(f"  Carpetas eliminadas: {deleted_folders}")
    print(f"\n{GREEN}Archivos esenciales conservados:{RESET}")
    print("  ✓ app.py")
    print("  ✓ wsgi.py")
    print("  ✓ requirements.txt")
    print("  ✓ config.py")
    print("  ✓ database/")
    print("  ✓ templates/")
    print("  ✓ static/")
    print("  ✓ uploads/")
    print(f"\n{YELLOW}{'='*60}\n{RESET}")

if __name__ == '__main__':
    main()
