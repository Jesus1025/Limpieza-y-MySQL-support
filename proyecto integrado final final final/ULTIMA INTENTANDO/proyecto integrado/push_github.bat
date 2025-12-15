@echo off
cd /d "d:\Escritorio\proyecto integrado final final final\ULTIMA INTENTANDO\proyecto integrado"
"C:\Program Files\Git\bin\git.exe" add -A
"C:\Program Files\Git\bin\git.exe" commit -m "Arreglo: Agregar clientes con MySQL en PythonAnywhere - endpoints compatibles con MySQL y SQLite"
"C:\Program Files\Git\bin\git.exe" push origin main
echo.
echo ========================================
echo CODIGO SUBIDO A GITHUB EXITOSAMENTE
echo ========================================
pause
