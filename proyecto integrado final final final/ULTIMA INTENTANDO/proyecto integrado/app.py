# ============================================================
# TEKNETAU - Sistema de Gestión
# 100% MySQL - PythonAnywhere
# ============================================================

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, Response
import os
import io
import csv
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

# ============================================================
# CONFIGURACIÓN
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'teknetau_secretkey_2025')

# MySQL PythonAnywhere - HARDCODED para evitar problemas
MYSQL_CONFIG = {
    'host': 'Teknetautest.mysql.pythonanywhere-services.com',
    'user': 'Teknetautest',
    'password': '19101810Aa',
    'database': 'Teknetautest$default',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


def get_db():
    """Conexión a MySQL"""
    return pymysql.connect(**MYSQL_CONFIG)


# ============================================================
# VALIDACIONES SIMPLES
# ============================================================

import re

def normalize_rut(rut):
    if not rut:
        return ''
    clean = rut.upper().replace('.', '').replace('-', '').replace(' ', '').strip()
    if len(clean) < 2:
        return ''
    return f"{clean[:-1]}-{clean[-1]}"


def validate_rut(rut):
    if not rut:
        return False
    clean = rut.upper().replace('.', '').replace('-', '').replace(' ', '').strip()
    if len(clean) < 2:
        return False
    cuerpo = clean[:-1]
    dv = clean[-1]
    if not cuerpo.isdigit():
        return False
    
    suma = 0
    mult = 2
    for c in reversed(cuerpo):
        suma += int(c) * mult
        mult = mult + 1 if mult < 7 else 2
    
    resto = suma % 11
    dv_calc = 11 - resto
    
    if dv_calc == 11:
        esperado = '0'
    elif dv_calc == 10:
        esperado = 'K'
    else:
        esperado = str(dv_calc)
    
    return esperado == dv


def validate_email(email):
    """Validar formato de email"""
    if not email:
        return True  # Email es opcional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


# ============================================================
# DECORADORES
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Solo permite acceso a usuarios con rol 'admin'"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado'}), 401
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
            flash('No tienes permisos para acceder a esta sección', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def no_consulta(f):
    """Permite acceso a admin y usuario, pero NO a consulta"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado'}), 401
            return redirect(url_for('login'))
        if session.get('rol') == 'consulta':
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Acceso denegado. Usuario de solo consulta'}), 403
            flash('No tienes permisos para realizar esta acción', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# RUTAS DE PRUEBA
# ============================================================

@app.route('/api/test-documentos')
def test_documentos():
    """Ver documentos en la BD"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) as total FROM documentos")
        total = cur.fetchone()['total']
        
        cur.execute("SELECT * FROM documentos ORDER BY id DESC LIMIT 5")
        docs = cur.fetchall()
        
        # Convertir fechas a string
        for doc in docs:
            if doc.get('fecha_emision'):
                doc['fecha_emision'] = str(doc['fecha_emision'])
            if doc.get('fecha_creacion'):
                doc['fecha_creacion'] = str(doc['fecha_creacion'])
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_documentos': total,
            'ultimos_documentos': docs
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test-proyecto-docs/<codigo>')
def test_proyecto_docs(codigo):
    """Ver documentos de un proyecto específico para debug"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Ver todos los documentos con proyecto_codigo
        cur.execute("SELECT id, numero_doc, tipo_doc, proyecto_codigo FROM documentos WHERE proyecto_codigo IS NOT NULL")
        docs_con_proyecto = cur.fetchall()
        
        # Ver documentos del proyecto específico
        cur.execute("SELECT id, numero_doc, tipo_doc, proyecto_codigo FROM documentos WHERE proyecto_codigo = %s", (codigo,))
        docs_del_proyecto = cur.fetchall()
        
        conn.close()
        
        return jsonify({
            'codigo_buscado': codigo,
            'docs_con_cualquier_proyecto': docs_con_proyecto,
            'docs_del_proyecto_especifico': docs_del_proyecto
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-insert')
def test_insert():
    """Insertar cliente de prueba directamente"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Intentar insertar cliente de prueba
        cur.execute('''
            INSERT INTO clientes (rut, razon_social, giro, telefono, email, direccion, activo)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        ''', ('11111111-1', 'CLIENTE PRUEBA', 'Servicios', '+56912345678', 'test@test.cl', 'Direccion Test'))
        
        conn.commit()
        
        # Verificar que se insertó
        cur.execute("SELECT COUNT(*) as total FROM clientes")
        total = cur.fetchone()['total']
        
        cur.execute("SELECT * FROM clientes ORDER BY id DESC LIMIT 1")
        ultimo = cur.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Cliente de prueba insertado',
            'total_clientes': total,
            'ultimo_cliente': ultimo
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test-db')
def test_db():
    """Probar conexión y ver estructura"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SHOW TABLES")
        tables = [list(t.values())[0] for t in cur.fetchall()]
        
        cur.execute("DESCRIBE clientes")
        clientes_struct = cur.fetchall()
        
        cur.execute("DESCRIBE usuarios")
        usuarios_struct = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) as total FROM clientes")
        total_clientes = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM usuarios")
        total_usuarios = cur.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'tables': tables,
            'clientes_estructura': clientes_struct,
            'usuarios_estructura': usuarios_struct,
            'total_clientes': total_clientes,
            'total_usuarios': total_usuarios
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sync-tables')
def sync_tables():
    """Agregar columnas faltantes a tablas existentes"""
    try:
        conn = get_db()
        cur = conn.cursor()
        results = []
        
        # Verificar y agregar columnas faltantes a clientes
        columnas_clientes = {
            'giro': "ALTER TABLE clientes ADD COLUMN giro VARCHAR(150)",
            'telefono': "ALTER TABLE clientes ADD COLUMN telefono VARCHAR(30)",
            'email': "ALTER TABLE clientes ADD COLUMN email VARCHAR(150)",
            'direccion': "ALTER TABLE clientes ADD COLUMN direccion VARCHAR(300)",
            'comuna': "ALTER TABLE clientes ADD COLUMN comuna VARCHAR(100)",
            'cuenta_corriente': "ALTER TABLE clientes ADD COLUMN cuenta_corriente VARCHAR(50)",
            'banco': "ALTER TABLE clientes ADD COLUMN banco VARCHAR(100)",
            'observaciones': "ALTER TABLE clientes ADD COLUMN observaciones TEXT",
            'activo': "ALTER TABLE clientes ADD COLUMN activo TINYINT(1) DEFAULT 1",
            'fecha_creacion': "ALTER TABLE clientes ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        cur.execute("DESCRIBE clientes")
        cols_existentes = {col['Field'] for col in cur.fetchall()}
        
        for col, sql in columnas_clientes.items():
            if col not in cols_existentes:
                try:
                    cur.execute(sql)
                    results.append(f"Agregada columna clientes.{col}")
                except Exception as e:
                    results.append(f"Error en clientes.{col}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'results': results,
            'message': 'Sincronización completada'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/crear-tablas')
def crear_tablas():
    """Crear/recrear tablas necesarias"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Tabla usuarios
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(200),
                email VARCHAR(150),
                rol VARCHAR(50) DEFAULT 'usuario',
                activo TINYINT(1) DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla clientes
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INT PRIMARY KEY AUTO_INCREMENT,
                rut VARCHAR(20) UNIQUE NOT NULL,
                razon_social VARCHAR(200) NOT NULL,
                giro VARCHAR(150),
                telefono VARCHAR(30),
                email VARCHAR(150),
                direccion VARCHAR(300),
                comuna VARCHAR(100),
                cuenta_corriente VARCHAR(50),
                banco VARCHAR(100),
                observaciones TEXT,
                activo TINYINT(1) DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla proyectos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS proyectos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                cliente_rut VARCHAR(20),
                presupuesto DECIMAL(15,2) DEFAULT 0,
                fecha_inicio DATE,
                fecha_termino DATE,
                estado VARCHAR(50) DEFAULT 'Activo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla documentos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                numero_doc INT NOT NULL,
                tipo_doc VARCHAR(10) NOT NULL,
                fecha_emision DATE NOT NULL,
                cliente_rut VARCHAR(20),
                descripcion TEXT,
                valor_neto DECIMAL(15,2) DEFAULT 0,
                iva DECIMAL(15,2) DEFAULT 0,
                valor_total DECIMAL(15,2) DEFAULT 0,
                estado VARCHAR(50) DEFAULT 'Pendiente',
                forma_pago VARCHAR(50) DEFAULT 'Contado',
                proyecto_codigo VARCHAR(50),
                motivo_nc_nd VARCHAR(255),
                documento_referencia_id INT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Agregar columnas nuevas si no existen (para BD existentes)
        try:
            cur.execute("ALTER TABLE documentos ADD COLUMN motivo_nc_nd VARCHAR(255)")
        except:
            pass  # Columna ya existe
        try:
            cur.execute("ALTER TABLE documentos ADD COLUMN documento_referencia_id INT")
        except:
            pass  # Columna ya existe
        
        # Crear usuario admin si no existe
        pwd = generate_password_hash('admin123', method='pbkdf2:sha256')
        cur.execute('''
            INSERT IGNORE INTO usuarios (username, password_hash, nombre, email, rol, activo)
            VALUES ('admin', %s, 'Administrador', 'admin@teknetau.cl', 'admin', 1)
        ''', (pwd,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Tablas creadas correctamente',
            'usuario': 'admin',
            'password': 'admin123'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# LOGIN / LOGOUT
# ============================================================

@app.route('/api/migrar-bd')
def migrar_bd():
    """Migrar base de datos - agregar columnas nuevas"""
    try:
        conn = get_db()
        cur = conn.cursor()
        resultados = []
        
        # Verificar si la columna motivo_nc_nd existe
        cur.execute("""
            SELECT COUNT(*) as existe FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'documentos' 
            AND column_name = 'motivo_nc_nd'
        """)
        if cur.fetchone()['existe'] == 0:
            cur.execute("ALTER TABLE documentos ADD COLUMN motivo_nc_nd VARCHAR(255)")
            resultados.append('Columna motivo_nc_nd agregada')
        else:
            resultados.append('Columna motivo_nc_nd ya existe')
        
        # Verificar si la columna documento_referencia_id existe
        cur.execute("""
            SELECT COUNT(*) as existe FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'documentos' 
            AND column_name = 'documento_referencia_id'
        """)
        if cur.fetchone()['existe'] == 0:
            cur.execute("ALTER TABLE documentos ADD COLUMN documento_referencia_id INT")
            resultados.append('Columna documento_referencia_id agregada')
        else:
            resultados.append('Columna documento_referencia_id ya existe')
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Migración completada',
            'resultados': resultados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE username = %s AND activo = 1', (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nombre'] = user['nombre']
            session['rol'] = user['rol'] or 'usuario'
            flash(f"Bienvenido {user['nombre']}", 'success')
            return redirect(url_for('index'))
        
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ============================================================
# PÁGINAS PRINCIPALES
# ============================================================

@app.route('/')
@login_required
def index():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) as t FROM clientes WHERE activo=1")
        tc = cur.fetchone()['t']
        
        cur.execute("SELECT COUNT(*) as t FROM proyectos WHERE estado='Activo'")
        tp = cur.fetchone()['t']
        
        cur.execute("SELECT COUNT(*) as t FROM documentos WHERE estado='Pendiente'")
        dp = cur.fetchone()['t']
        
        cur.execute("SELECT COALESCE(SUM(valor_total),0) as t FROM documentos WHERE estado='Pendiente'")
        dt = cur.fetchone()['t'] or 0
        
        stats = {'total_clientes': tc, 'total_proyectos': tp, 'documentos_pendientes': dp, 'deuda_total': dt}
        
        cur.execute('''
            SELECT d.*, c.razon_social FROM documentos d 
            LEFT JOIN clientes c ON d.cliente_rut = c.rut 
            ORDER BY d.fecha_emision DESC LIMIT 5
        ''')
        docs = cur.fetchall()
        
        cur.execute("SELECT rut, razon_social FROM clientes WHERE activo=1")
        clientes = cur.fetchall()
        
        return render_template('index.html', stats=stats, documentos=docs, clientes=clientes)
    except:
        return render_template('index.html', stats={'total_clientes':0,'total_proyectos':0,'documentos_pendientes':0,'deuda_total':0}, documentos=[], clientes=[])
    finally:
        conn.close()


@app.route('/clientes')
@login_required
def clientes():
    bancos = ['Banco de Chile','BCI','Scotiabank','Santander','Banco Estado','Itaú','BBVA','Otro']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes WHERE activo=1 ORDER BY razon_social")
    lista = cur.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=lista, bancos=bancos)


@app.route('/proyectos')
@login_required
def proyectos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT p.*, c.razon_social FROM proyectos p LEFT JOIN clientes c ON p.cliente_rut=c.rut ORDER BY p.nombre')
    plist = cur.fetchall()
    cur.execute('SELECT rut, razon_social FROM clientes WHERE activo=1')
    clist = cur.fetchall()
    conn.close()
    return render_template('proyectos.html', proyectos=plist, clientes=clist)


@app.route('/facturas')
@login_required
def facturas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rut, razon_social FROM clientes WHERE activo=1")
    clientes = cur.fetchall()
    cur.execute("SELECT codigo, nombre FROM proyectos WHERE estado='Activo'")
    proyectos = cur.fetchall()
    cur.execute("SELECT COALESCE(MAX(numero_doc),0) as u FROM documentos WHERE tipo_doc='FAC'")
    ult = cur.fetchone()['u']
    conn.close()
    return render_template('facturas.html', clientes=clientes, proyectos=proyectos, proximo_numero=ult+1, today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/boletas')
@login_required
def boletas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rut, razon_social FROM clientes WHERE activo=1")
    clientes = cur.fetchall()
    cur.execute("SELECT codigo, nombre FROM proyectos WHERE estado='Activo'")
    proyectos = cur.fetchall()
    cur.execute("SELECT COALESCE(MAX(numero_doc),0) as u FROM documentos WHERE tipo_doc='BOL'")
    ult = cur.fetchone()['u']
    conn.close()
    return render_template('boletas.html', clientes=clientes, proyectos=proyectos, proximo_numero=ult+1, today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/notas-credito')
@login_required
def notas_credito():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rut, razon_social FROM clientes WHERE activo=1")
    clientes = cur.fetchall()
    
    # Obtener documentos que pueden ser referenciados (Facturas y Boletas)
    cur.execute("""
        SELECT d.id, d.numero_doc, d.tipo_doc, d.valor_total, c.razon_social 
        FROM documentos d 
        LEFT JOIN clientes c ON d.cliente_rut = c.rut 
        WHERE d.tipo_doc IN ('FAC', 'BOL') AND d.estado != 'Anulado'
        ORDER BY d.fecha_emision DESC LIMIT 100
    """)
    documentos_referencia = cur.fetchall()
    
    # Próximo número de NC
    cur.execute("SELECT COALESCE(MAX(numero_doc),0) as u FROM documentos WHERE tipo_doc='NC'")
    ult = cur.fetchone()['u']
    
    conn.close()
    
    # Motivos estándar para NC según SII Chile
    motivos = [
        {'codigo': '1', 'descripcion': 'Anula documento de referencia'},
        {'codigo': '2', 'descripcion': 'Corrige texto del documento de referencia'},
        {'codigo': '3', 'descripcion': 'Corrige monto del documento de referencia'},
        {'codigo': '4', 'descripcion': 'Devolución de mercadería'},
        {'codigo': '5', 'descripcion': 'Descuento o bonificación'},
        {'codigo': '6', 'descripcion': 'Resciliación de contrato'},
        {'codigo': '7', 'descripcion': 'Ajuste de precio'},
    ]
    
    return render_template('notas_credito.html', 
                         clientes=clientes, 
                         documentos_referencia=documentos_referencia,
                         motivos=motivos,
                         proximo_numero=ult+1, 
                         today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/notas-debito')
@login_required
def notas_debito():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rut, razon_social FROM clientes WHERE activo=1")
    clientes = cur.fetchall()
    
    # Obtener documentos que pueden ser referenciados (Facturas y Boletas)
    cur.execute("""
        SELECT d.id, d.numero_doc, d.tipo_doc, d.valor_total, c.razon_social 
        FROM documentos d 
        LEFT JOIN clientes c ON d.cliente_rut = c.rut 
        WHERE d.tipo_doc IN ('FAC', 'BOL') AND d.estado != 'Anulado'
        ORDER BY d.fecha_emision DESC LIMIT 100
    """)
    documentos_referencia = cur.fetchall()
    
    # Próximo número de ND
    cur.execute("SELECT COALESCE(MAX(numero_doc),0) as u FROM documentos WHERE tipo_doc='ND'")
    ult = cur.fetchone()['u']
    
    conn.close()
    
    # Motivos estándar para ND según SII Chile
    motivos = [
        {'codigo': '1', 'descripcion': 'Intereses por mora'},
        {'codigo': '2', 'descripcion': 'Gastos de cobranza'},
        {'codigo': '3', 'descripcion': 'Diferencia de precio'},
        {'codigo': '4', 'descripcion': 'Cargo por servicio adicional'},
        {'codigo': '5', 'descripcion': 'Ajuste de precio'},
        {'codigo': '6', 'descripcion': 'Recargo por flete'},
        {'codigo': '7', 'descripcion': 'Devolución de descuento'},
        {'codigo': '8', 'descripcion': 'Devolución'},
        {'codigo': '9', 'descripcion': 'Otros cargos'},
    ]
    
    return render_template('notas_debito.html', 
                         clientes=clientes, 
                         documentos_referencia=documentos_referencia,
                         motivos=motivos,
                         proximo_numero=ult+1, 
                         today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/reportes')
@login_required
def reportes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT codigo, nombre, estado FROM proyectos ORDER BY nombre')
    proyectos = cur.fetchall()
    conn.close()
    return render_template('reportes.html', proyectos=proyectos)


@app.route('/administracion')
@login_required
def administracion():
    return render_template('administracion.html')


# ============================================================
# API USUARIOS/PERFILES
# ============================================================

@app.route('/api/usuarios', methods=['GET', 'POST'])
@app.route('/api/usuarios-dev', methods=['GET', 'POST'])
@admin_required
def api_usuarios():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        if request.method == 'GET':
            cur.execute('SELECT id, username, nombre, email, rol, activo, fecha_creacion FROM usuarios ORDER BY username')
            return jsonify(cur.fetchall())
        
        # POST - crear usuario
        data = request.get_json() or {}
        username = (data.get('username') or '').strip().lower()
        nombre = (data.get('nombre') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password', '')
        rol = data.get('rol', 'usuario')
        activo = 1 if data.get('activo', True) else 0
        
        if not username or not nombre:
            return jsonify({'success': False, 'error': 'Usuario y nombre son obligatorios'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'success': False, 'error': 'Contraseña debe tener mínimo 8 caracteres'}), 400
        
        # Verificar si existe
        cur.execute('SELECT id FROM usuarios WHERE username=%s', (username,))
        if cur.fetchone():
            return jsonify({'success': False, 'error': 'El usuario ya existe'}), 400
        
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        cur.execute('''
            INSERT INTO usuarios (username, password_hash, nombre, email, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (username, password_hash, nombre, email, rol, activo))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Usuario creado'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/usuarios/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/usuarios-dev/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def api_usuario_detalle(user_id):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        if request.method == 'GET':
            cur.execute('SELECT id, username, nombre, email, rol, activo FROM usuarios WHERE id=%s', (user_id,))
            user = cur.fetchone()
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            return jsonify(user)
        
        if request.method == 'DELETE':
            # No permitir eliminar el propio usuario
            if user_id == session.get('user_id'):
                return jsonify({'success': False, 'error': 'No puedes eliminar tu propio usuario'}), 400
            
            cur.execute('DELETE FROM usuarios WHERE id=%s', (user_id,))
            conn.commit()
            return jsonify({'success': True})
        
        # PUT - actualizar usuario
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password', '')
        rol = data.get('rol', 'usuario')
        activo = 1 if data.get('activo', True) else 0
        
        if password and len(password) >= 8:
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            cur.execute('''
                UPDATE usuarios SET nombre=%s, email=%s, password_hash=%s, rol=%s, activo=%s WHERE id=%s
            ''', (nombre, email, password_hash, rol, activo, user_id))
        else:
            cur.execute('''
                UPDATE usuarios SET nombre=%s, email=%s, rol=%s, activo=%s WHERE id=%s
            ''', (nombre, email, rol, activo, user_id))
        
        conn.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/cambiar-password', methods=['POST'])
@login_required
def api_cambiar_password():
    data = request.get_json() or {}
    password_actual = data.get('password_actual', '')
    password_nueva = data.get('password_nueva', '')
    
    if not password_actual or not password_nueva:
        return jsonify({'success': False, 'error': 'Ambas contraseñas son requeridas'}), 400
    
    if len(password_nueva) < 8:
        return jsonify({'success': False, 'error': 'La nueva contraseña debe tener mínimo 8 caracteres'}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute('SELECT password_hash FROM usuarios WHERE id=%s', (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not check_password_hash(user['password_hash'], password_actual):
            return jsonify({'success': False, 'error': 'Contraseña actual incorrecta'}), 400
        
        nuevo_hash = generate_password_hash(password_nueva, method='pbkdf2:sha256')
        cur.execute('UPDATE usuarios SET password_hash=%s WHERE id=%s', (nuevo_hash, session['user_id']))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Contraseña actualizada'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    if request.method == 'POST':
        actual = request.form.get('password_actual')
        nueva = request.form.get('nuevo_password')
        confirmar = request.form.get('confirmar_password')
        
        if nueva != confirmar:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('cambiar_password'))
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT password_hash FROM usuarios WHERE id=%s', (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not check_password_hash(user['password_hash'], actual):
            flash('Contraseña actual incorrecta', 'error')
            conn.close()
            return redirect(url_for('cambiar_password'))
        
        nuevo_hash = generate_password_hash(nueva, method='pbkdf2:sha256')
        cur.execute('UPDATE usuarios SET password_hash=%s WHERE id=%s', (nuevo_hash, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Contraseña actualizada', 'success')
        return redirect(url_for('index'))
    
    return render_template('cambiar_password.html')


# ============================================================
# API CLIENTES
# ============================================================

@app.route('/api/clientes', methods=['GET', 'POST', 'DELETE'])
@app.route('/api/clientes-dev', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_clientes():
    # Verificar permisos para operaciones de escritura
    if request.method in ['POST', 'DELETE'] and session.get('rol') == 'consulta':
        return jsonify({'error': 'Acceso denegado. Usuario de solo consulta'}), 403
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        if request.method == 'GET':
            estado = request.args.get('estado', '').lower()
            if estado == 'activo':
                cur.execute("SELECT * FROM clientes WHERE activo=1 ORDER BY razon_social")
            elif estado == 'inactivo':
                cur.execute("SELECT * FROM clientes WHERE activo=0 ORDER BY razon_social")
            else:
                cur.execute("SELECT * FROM clientes ORDER BY razon_social")
            return jsonify(cur.fetchall())
        
        if request.method == 'DELETE':
            rut = request.args.get('rut')
            if not rut:
                return jsonify({'success': False, 'error': 'RUT requerido'}), 400
            rut_n = normalize_rut(rut)
            cur.execute('UPDATE clientes SET activo=0 WHERE rut=%s', (rut_n,))
            conn.commit()
            return jsonify({'success': True})
        
        # POST - Crear nuevo cliente
        data = request.get_json() or {}
        rut = (data.get('rut') or '').strip()
        razon = (data.get('razon_social') or '').strip()
        email = (data.get('email') or '').strip()
        
        # Validaciones obligatorias
        if not rut or not razon:
            return jsonify({'success': False, 'error': 'RUT y Razón Social son obligatorios'}), 400
        
        # Validar formato RUT y dígito verificador
        if not validate_rut(rut):
            return jsonify({'success': False, 'error': 'RUT inválido. Verifique el dígito verificador.'}), 400
        
        # Validar formato email si se proporciona
        if email and not validate_email(email):
            return jsonify({'success': False, 'error': 'Formato de email inválido'}), 400
        
        rut_n = normalize_rut(rut)
        
        # Verificar si el RUT ya existe
        cur.execute("SELECT id, activo FROM clientes WHERE rut=%s", (rut_n,))
        existe = cur.fetchone()
        
        if existe:
            # Si existe y está activo, rechazar
            if existe['activo'] == 1:
                return jsonify({'success': False, 'error': f'El RUT {rut_n} ya está registrado'}), 400
            # Si existe pero está inactivo, reactivar y actualizar
            cur.execute('''
                UPDATE clientes SET 
                    razon_social=%s, giro=%s, telefono=%s, email=%s, 
                    direccion=%s, comuna=%s, cuenta_corriente=%s, banco=%s, 
                    observaciones=%s, activo=1
                WHERE rut=%s
            ''', (
                razon,
                data.get('giro', ''),
                data.get('telefono', ''),
                email,
                data.get('direccion', ''),
                data.get('comuna', ''),
                data.get('cuenta_corriente', ''),
                data.get('banco', ''),
                data.get('observaciones', ''),
                rut_n
            ))
            msg = 'Cliente reactivado'
        else:
            # Crear nuevo cliente
            cur.execute('''
                INSERT INTO clientes (rut, razon_social, giro, telefono, email, direccion, comuna, cuenta_corriente, banco, observaciones, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            ''', (
                rut_n,
                razon,
                data.get('giro', ''),
                data.get('telefono', ''),
                email,
                data.get('direccion', ''),
                data.get('comuna', ''),
                data.get('cuenta_corriente', ''),
                data.get('banco', ''),
                data.get('observaciones', '')
            ))
            msg = 'Cliente creado'
        
        conn.commit()
        return jsonify({'success': True, 'message': msg})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/clientes/<rut>/toggle-activo', methods=['PUT'])
@app.route('/api/clientes-dev/<rut>/toggle-activo', methods=['PUT'])
@no_consulta
def api_cliente_toggle_activo(rut):
    conn = get_db()
    cur = conn.cursor()
    rut_n = normalize_rut(rut)
    
    try:
        # Obtener estado actual
        cur.execute("SELECT activo FROM clientes WHERE rut=%s", (rut_n,))
        cliente = cur.fetchone()
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        nuevo_estado = 0 if cliente['activo'] == 1 else 1
        cur.execute("UPDATE clientes SET activo=%s WHERE rut=%s", (nuevo_estado, rut_n))
        conn.commit()
        
        return jsonify({'success': True, 'activo': nuevo_estado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/clientes/<rut>', methods=['GET', 'PUT'])
@app.route('/api/clientes-dev/<rut>', methods=['GET', 'PUT'])
def api_cliente_detalle(rut):
    conn = get_db()
    cur = conn.cursor()
    rut_n = normalize_rut(rut)
    
    try:
        if request.method == 'GET':
            cur.execute("SELECT * FROM clientes WHERE rut=%s", (rut_n,))
            cliente = cur.fetchone()
            if not cliente:
                return jsonify({'error': 'No encontrado'}), 404
            return jsonify(cliente)
        
        # PUT
        data = request.get_json() or {}
        cur.execute('''
            UPDATE clientes SET 
                razon_social=%s, giro=%s, telefono=%s, email=%s, 
                direccion=%s, comuna=%s, cuenta_corriente=%s, banco=%s, observaciones=%s
            WHERE rut=%s
        ''', (
            data.get('razon_social', ''),
            data.get('giro', ''),
            data.get('telefono', ''),
            data.get('email', ''),
            data.get('direccion', ''),
            data.get('comuna', ''),
            data.get('cuenta_corriente', ''),
            data.get('banco', ''),
            data.get('observaciones', ''),
            rut_n
        ))
        conn.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ============================================================
# API PROYECTOS
# ============================================================

@app.route('/api/proyectos', methods=['GET', 'POST'])
@login_required
def api_proyectos():
    # Verificar permisos para operaciones de escritura
    if request.method == 'POST' and session.get('rol') == 'consulta':
        return jsonify({'error': 'Acceso denegado. Usuario de solo consulta'}), 403
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        if request.method == 'GET':
            cur.execute('SELECT p.*, c.razon_social FROM proyectos p LEFT JOIN clientes c ON p.cliente_rut=c.rut ORDER BY p.id DESC')
            return jsonify(cur.fetchall())
        
        data = request.get_json() or {}
        codigo = (data.get('codigo') or '').strip()
        nombre = (data.get('nombre') or '').strip()
        cliente_rut = normalize_rut(data.get('cliente_rut', ''))
        
        if not codigo or not nombre:
            return jsonify({'success': False, 'error': 'Código y nombre son obligatorios'}), 400
        
        cur.execute('SELECT id FROM proyectos WHERE codigo=%s', (codigo,))
        existe = cur.fetchone()
        
        if existe:
            cur.execute('''
                UPDATE proyectos SET nombre=%s, descripcion=%s, cliente_rut=%s, presupuesto=%s, 
                fecha_inicio=%s, fecha_termino=%s, estado=%s WHERE codigo=%s
            ''', (
                nombre, data.get('descripcion',''), cliente_rut, 
                float(data.get('presupuesto',0) or 0),
                data.get('fecha_inicio'), data.get('fecha_termino'),
                data.get('estado','Activo'), codigo
            ))
        else:
            cur.execute('''
                INSERT INTO proyectos (codigo, nombre, descripcion, cliente_rut, presupuesto, fecha_inicio, fecha_termino, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                codigo, nombre, data.get('descripcion',''), cliente_rut,
                float(data.get('presupuesto',0) or 0),
                data.get('fecha_inicio'), data.get('fecha_termino'),
                data.get('estado','Activo')
            ))
        
        conn.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/proyectos/<codigo>/toggle-estado', methods=['PUT'])
@no_consulta
def api_proyecto_toggle_estado(codigo):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT estado FROM proyectos WHERE codigo=%s", (codigo,))
        proyecto = cur.fetchone()
        if not proyecto:
            return jsonify({'success': False, 'error': 'Proyecto no encontrado'}), 404
        
        # Cambiar entre Activo e Inactivo
        nuevo_estado = 'Inactivo' if proyecto['estado'] == 'Activo' else 'Activo'
        cur.execute("UPDATE proyectos SET estado=%s WHERE codigo=%s", (nuevo_estado, codigo))
        conn.commit()
        
        return jsonify({'success': True, 'estado': nuevo_estado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/proyectos/<codigo>', methods=['PUT', 'DELETE'])
@no_consulta
def api_proyecto_detalle(codigo):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        if request.method == 'DELETE':
            cur.execute('DELETE FROM proyectos WHERE codigo=%s', (codigo,))
            conn.commit()
            return jsonify({'success': True})
        
        data = request.get_json() or {}
        cur.execute('''
            UPDATE proyectos SET nombre=%s, descripcion=%s, cliente_rut=%s, presupuesto=%s,
            fecha_inicio=%s, fecha_termino=%s, estado=%s WHERE codigo=%s
        ''', (
            data.get('nombre',''), data.get('descripcion',''),
            normalize_rut(data.get('cliente_rut','')),
            float(data.get('presupuesto',0) or 0),
            data.get('fecha_inicio'), data.get('fecha_termino'),
            data.get('estado','Activo'), codigo
        ))
        conn.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ============================================================
# API DOCUMENTOS DE REFERENCIA (para NC/ND)
# ============================================================

@app.route('/api/documentos-referencia/<rut>')
@login_required
def api_documentos_referencia(rut):
    """Obtener documentos que pueden ser referenciados por NC/ND para un cliente"""
    conn = get_db()
    cur = conn.cursor()
    rut_n = normalize_rut(rut)
    
    try:
        cur.execute("""
            SELECT id, numero_doc, tipo_doc, fecha_emision, valor_total, estado
            FROM documentos 
            WHERE cliente_rut = %s 
            AND tipo_doc IN ('FAC', 'BOL') 
            AND estado != 'Anulado'
            ORDER BY fecha_emision DESC
            LIMIT 50
        """, (rut_n,))
        
        documentos = cur.fetchall()
        
        # Convertir fechas a string
        for doc in documentos:
            if doc.get('fecha_emision'):
                doc['fecha_emision'] = str(doc['fecha_emision'])
        
        return jsonify(documentos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# ============================================================
# API DOCUMENTOS
# ============================================================

@app.route('/api/generar-documento', methods=['POST'])
@no_consulta
def api_generar_documento():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data.get('numero_doc'):
            return jsonify({'success': False, 'error': 'Número de documento requerido'}), 400
        if not data.get('cliente_rut'):
            return jsonify({'success': False, 'error': 'Cliente requerido'}), 400
        if not data.get('tipo_doc'):
            return jsonify({'success': False, 'error': 'Tipo de documento requerido'}), 400
        
        # Verificar que no exista el número de documento para ese tipo
        cur.execute('SELECT id FROM documentos WHERE numero_doc=%s AND tipo_doc=%s', 
                   (data['numero_doc'], data['tipo_doc']))
        if cur.fetchone():
            return jsonify({'success': False, 'error': f"Ya existe {data['tipo_doc']} con número {data['numero_doc']}"}), 400
        
        # El estado para NC y ND puede venir del frontend
        estado_doc = data.get('estado', 'Pendiente')
        if data['tipo_doc'] in ('NC', 'ND') and not data.get('estado'):
            estado_doc = 'Aplicada'
        
        cur.execute('''
            INSERT INTO documentos (numero_doc, tipo_doc, fecha_emision, cliente_rut, descripcion, valor_neto, iva, valor_total, estado, forma_pago, proyecto_codigo, motivo_nc_nd)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['numero_doc'], 
            data['tipo_doc'], 
            data.get('fecha_emision') or datetime.now().strftime('%Y-%m-%d'),
            data['cliente_rut'], 
            data.get('descripcion', ''),
            data.get('valor_neto', 0), 
            data.get('iva', 0), 
            data.get('valor_total', 0),
            estado_doc,
            data.get('forma_pago', 'Contado'), 
            data.get('proyecto_codigo') or None,
            data.get('motivo_nc_nd') or None
        ))
        conn.commit()
        doc_id = cur.lastrowid
        return jsonify({'success': True, 'message': 'Documento generado correctamente', 'documento_id': doc_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/documentos-pendientes')
@login_required
def api_docs_pendientes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.cliente_rut,
               d.valor_neto, d.iva, d.valor_total, d.estado, d.proyecto_codigo,
               c.razon_social
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE d.estado='Pendiente' ORDER BY d.fecha_emision DESC
    ''')
    docs = cur.fetchall()
    conn.close()
    
    # Formatear fechas
    for doc in docs:
        if doc.get('fecha_emision'):
            doc['fecha_emision'] = str(doc['fecha_emision'])
    
    return jsonify({'documentos': docs})


@app.route('/api/documentos/<int:doc_id>/estado', methods=['PUT'])
@no_consulta
def api_doc_estado(doc_id):
    data = request.get_json() or {}
    estado = data.get('estado', '')
    
    if estado not in ['Pendiente', 'Pagado', 'Anulado', 'Aplicada']:
        return jsonify({'success': False, 'error': 'Estado inválido'}), 400
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE documentos SET estado=%s WHERE id=%s', (estado, doc_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ============================================================
# API REPORTES
# ============================================================

@app.route('/api/reporte-deudas')
@login_required
def api_reporte_deudas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT c.rut as cliente_rut, c.razon_social, COUNT(d.id) as cantidad_docs, COALESCE(SUM(d.valor_total),0) as total_deuda
        FROM clientes c
        LEFT JOIN documentos d ON c.rut=d.cliente_rut AND d.estado='Pendiente'
        WHERE c.activo=1 GROUP BY c.rut, c.razon_social HAVING total_deuda > 0
        ORDER BY total_deuda DESC
    ''')
    result = cur.fetchall()
    conn.close()
    return jsonify({'deudas': result})


@app.route('/api/reporte-resumen')
@login_required
def api_reporte_resumen():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT COALESCE(SUM(valor_total),0) as t FROM documentos WHERE tipo_doc IN ('FAC','BOL')")
    facturado = cur.fetchone()['t']
    
    cur.execute("SELECT COALESCE(SUM(valor_total),0) as t FROM documentos WHERE estado='Pagado'")
    pagado = cur.fetchone()['t']
    
    cur.execute("SELECT COALESCE(SUM(valor_total),0) as t FROM documentos WHERE estado='Pendiente'")
    pendiente = cur.fetchone()['t']
    
    cur.execute("SELECT COUNT(*) as c FROM documentos")
    total = cur.fetchone()['c']
    
    conn.close()
    return jsonify({
        'total_facturado': facturado,
        'total_pagado': pagado,
        'total_pendiente': pendiente,
        'total_documentos': total
    })


@app.route('/api/buscar-documentos')
@login_required
def api_buscar_documentos():
    """Buscar documentos con filtros"""
    tipo_doc = request.args.get('tipo_doc', '')
    estado = request.args.get('estado', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    proyecto = request.args.get('proyecto', '')
    
    conn = get_db()
    cur = conn.cursor()
    
    query = '''
        SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.cliente_rut,
               d.descripcion, d.valor_neto, d.iva, d.valor_total, d.estado, 
               d.proyecto_codigo, c.razon_social
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE 1=1
    '''
    params = []
    
    if tipo_doc:
        query += ' AND d.tipo_doc=%s'
        params.append(tipo_doc)
    if estado:
        query += ' AND d.estado=%s'
        params.append(estado)
    if fecha_desde:
        query += ' AND d.fecha_emision >= %s'
        params.append(fecha_desde)
    if fecha_hasta:
        query += ' AND d.fecha_emision <= %s'
        params.append(fecha_hasta)
    if proyecto:
        query += ' AND d.proyecto_codigo=%s'
        params.append(proyecto)
    
    query += ' ORDER BY d.fecha_emision DESC, d.id DESC LIMIT 500'
    
    cur.execute(query, params)
    docs = cur.fetchall()
    conn.close()
    
    # Formatear fechas
    for doc in docs:
        if doc.get('fecha_emision'):
            doc['fecha_emision'] = str(doc['fecha_emision'])
    
    return jsonify({'documentos': docs})


@app.route('/api/proyecto/<codigo>/progreso')
@login_required
def api_proyecto_progreso(codigo):
    """Obtener progreso financiero de un proyecto"""
    conn = get_db()
    cur = conn.cursor()
    
    # Datos del proyecto
    cur.execute('''
        SELECT p.*, c.razon_social 
        FROM proyectos p 
        LEFT JOIN clientes c ON p.cliente_rut=c.rut 
        WHERE p.codigo=%s
    ''', (codigo,))
    proyecto = cur.fetchone()
    
    if not proyecto:
        conn.close()
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Documentos del proyecto - usar LIKE para asegurar match
    cur.execute('''
        SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.valor_total, 
               d.estado, c.razon_social, d.proyecto_codigo
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE d.proyecto_codigo = %s
        ORDER BY d.fecha_emision DESC
    ''', (codigo,))
    documentos = cur.fetchall()
    
    # Calcular totales
    cur.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN tipo_doc IN ('FAC','BOL') THEN valor_total ELSE 0 END), 0) as facturado,
            COALESCE(SUM(CASE WHEN estado='Pagado' THEN valor_total ELSE 0 END), 0) as cobrado,
            COALESCE(SUM(CASE WHEN estado='Pendiente' THEN valor_total ELSE 0 END), 0) as pendiente
        FROM documentos WHERE proyecto_codigo=%s
    ''', (codigo,))
    totales = cur.fetchone()
    
    conn.close()
    
    # Formatear fechas
    for doc in documentos:
        if doc.get('fecha_emision'):
            doc['fecha_emision'] = str(doc['fecha_emision'])
    
    presupuesto = float(proyecto.get('presupuesto') or 0)
    facturado = float(totales.get('facturado') or 0)
    cobrado = float(totales.get('cobrado') or 0)
    # El progreso se calcula en base a lo PAGADO (cobrado) vs presupuesto
    progreso = (cobrado / presupuesto * 100) if presupuesto > 0 else 0
    
    return jsonify({
        'proyecto': {
            'codigo': proyecto['codigo'],
            'nombre': proyecto['nombre'],
            'cliente': proyecto.get('razon_social', 'N/A'),
            'presupuesto': presupuesto,
            'estado': proyecto.get('estado', 'Activo')
        },
        'financiero': {
            'facturado': facturado,
            'cobrado': cobrado,
            'pendiente': float(totales.get('pendiente') or 0),
            'progreso': round(progreso, 1)
        },
        'documentos': documentos
    })


@app.route('/api/top-clientes')
@login_required
def api_top_clientes():
    """Top 10 clientes por facturación"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT c.rut, c.razon_social,
               COUNT(d.id) as cantidad_docs,
               COALESCE(SUM(d.valor_total), 0) as total_facturado,
               COALESCE(SUM(CASE WHEN d.estado='Pagado' THEN d.valor_total ELSE 0 END), 0) as total_pagado,
               COALESCE(SUM(CASE WHEN d.estado='Pendiente' THEN d.valor_total ELSE 0 END), 0) as total_pendiente
        FROM clientes c
        LEFT JOIN documentos d ON c.rut=d.cliente_rut AND d.tipo_doc IN ('FAC','BOL')
        WHERE c.activo=1
        GROUP BY c.rut, c.razon_social
        HAVING total_facturado > 0
        ORDER BY total_facturado DESC
        LIMIT 10
    ''')
    clientes = cur.fetchall()
    conn.close()
    
    return jsonify({'clientes': clientes})


@app.route('/api/cuentas-corrientes')
@login_required
def api_cuentas_corrientes():
    """Obtener lista de números de cuenta corriente únicos"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT cuenta_corriente FROM clientes WHERE cuenta_corriente IS NOT NULL AND cuenta_corriente != "" AND activo=1 ORDER BY cuenta_corriente')
    cuentas = [row['cuenta_corriente'] for row in cur.fetchall()]
    conn.close()
    return jsonify(cuentas)


@app.route('/api/clientes-por-cuenta/<cuenta>')
@login_required
def api_clientes_por_cuenta(cuenta):
    """Obtener clientes filtrados por número de cuenta corriente"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clientes WHERE cuenta_corriente=%s AND activo=1', (cuenta,))
    clientes = cur.fetchall()
    conn.close()
    return jsonify(clientes)


@app.route('/api/cuenta-corriente-detalle/<cuenta>')
@login_required
def api_cuenta_corriente_detalle(cuenta):
    """Obtener detalle completo de una cuenta corriente por número"""
    conn = get_db()
    cur = conn.cursor()
    
    # Obtener clientes con esta cuenta
    cur.execute('SELECT rut, razon_social, banco FROM clientes WHERE cuenta_corriente=%s AND activo=1', (cuenta,))
    clientes = cur.fetchall()
    
    if not clientes:
        conn.close()
        return jsonify({'error': 'No hay clientes con esta cuenta'}), 404
    
    ruts = [c['rut'] for c in clientes]
    placeholders = ','.join(['%s'] * len(ruts))
    
    # Obtener documentos de estos clientes
    cur.execute(f'''
        SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.cliente_rut,
               d.valor_total, d.estado, c.razon_social
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE d.cliente_rut IN ({placeholders})
        ORDER BY d.fecha_emision DESC
    ''', ruts)
    documentos = cur.fetchall()
    
    # Calcular totales
    cur.execute(f'''
        SELECT 
            COALESCE(SUM(CASE WHEN estado='Pagado' THEN valor_total ELSE 0 END), 0) as pagado,
            COALESCE(SUM(CASE WHEN estado='Pendiente' THEN valor_total ELSE 0 END), 0) as pendiente
        FROM documentos WHERE cliente_rut IN ({placeholders})
    ''', ruts)
    totales = cur.fetchone()
    
    conn.close()
    
    # Formatear fechas
    for doc in documentos:
        if doc.get('fecha_emision'):
            doc['fecha_emision'] = str(doc['fecha_emision'])
    
    return jsonify({
        'cuenta': cuenta,
        'clientes': clientes,
        'total_clientes': len(clientes),
        'documentos': documentos,
        'total_pagos': float(totales.get('pagado') or 0),
        'total_deudas': float(totales.get('pendiente') or 0)
    })


@app.route('/api/exportar-cuenta-corriente-csv/<cuenta>')
@login_required
def exportar_cuenta_corriente_csv(cuenta):
    """Exportar clientes y documentos de una cuenta corriente por número"""
    conn = get_db()
    cur = conn.cursor()
    
    # Obtener clientes con esta cuenta
    cur.execute('SELECT rut, razon_social FROM clientes WHERE cuenta_corriente=%s AND activo=1', (cuenta,))
    clientes = cur.fetchall()
    
    if not clientes:
        conn.close()
        return jsonify({'error': 'No hay clientes con esta cuenta'}), 404
    
    ruts = [c['rut'] for c in clientes]
    placeholders = ','.join(['%s'] * len(ruts))
    
    # Obtener documentos de estos clientes
    cur.execute(f'''
        SELECT d.tipo_doc, d.numero_doc, d.fecha_emision, c.razon_social,
               d.valor_neto, d.iva, d.valor_total, d.estado
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE d.cliente_rut IN ({placeholders})
        ORDER BY d.fecha_emision DESC
    ''', ruts)
    docs = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Tipo', 'N° Doc', 'Fecha', 'Cliente', 'Neto', 'IVA', 'Total', 'Estado'])
    for d in docs:
        writer.writerow([
            d['tipo_doc'], d['numero_doc'], str(d['fecha_emision']), d['razon_social'],
            d['valor_neto'], d['iva'], d['valor_total'], d['estado']
        ])
    
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=cuenta_{cuenta}.csv'}
    )


# ============================================================
# EXPORTAR CSV
# ============================================================

@app.route('/api/exportar-clientes-csv')
@login_required
def exportar_clientes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT rut, razon_social, giro, telefono, email, direccion, banco FROM clientes WHERE activo=1')
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['RUT', 'Razón Social', 'Giro', 'Teléfono', 'Email', 'Dirección', 'Banco'])
    for r in rows:
        writer.writerow([r['rut'], r['razon_social'], r['giro'], r['telefono'], r['email'], r['direccion'], r['banco']])
    
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=clientes.csv'}
    )


@app.route('/api/exportar-proyectos-csv')
@login_required
def exportar_proyectos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT p.codigo, p.nombre, p.descripcion, c.razon_social, p.presupuesto, p.estado FROM proyectos p LEFT JOIN clientes c ON p.cliente_rut=c.rut')
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Código', 'Nombre', 'Descripción', 'Cliente', 'Presupuesto', 'Estado'])
    for r in rows:
        writer.writerow([r['codigo'], r['nombre'], r['descripcion'], r['razon_social'], r['presupuesto'], r['estado']])
    
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=proyectos.csv'}
    )


@app.route('/api/exportar-deudas-excel')
@login_required
def exportar_deudas_excel():
    """Exportar deudas pendientes a CSV/Excel"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT c.rut, c.razon_social, COUNT(d.id) as cantidad_docs, COALESCE(SUM(d.valor_total),0) as total_deuda
        FROM clientes c
        LEFT JOIN documentos d ON c.rut=d.cliente_rut AND d.estado='Pendiente'
        WHERE c.activo=1 GROUP BY c.rut, c.razon_social HAVING total_deuda > 0
        ORDER BY total_deuda DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['RUT', 'Razón Social', 'Documentos Pendientes', 'Total Deuda'])
    for r in rows:
        writer.writerow([r['rut'], r['razon_social'], r['cantidad_docs'], r['total_deuda']])
    
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=deudas_pendientes.csv'}
    )


@app.route('/api/exportar-documentos-excel')
@login_required
def exportar_documentos_excel():
    """Exportar todos los documentos a CSV/Excel"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.tipo_doc, d.numero_doc, d.fecha_emision, c.razon_social, 
               d.descripcion, d.valor_neto, d.iva, d.valor_total, d.estado, d.proyecto_codigo
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        ORDER BY d.fecha_emision DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Tipo', 'N° Doc', 'Fecha', 'Cliente', 'Descripción', 'Neto', 'IVA', 'Total', 'Estado', 'Proyecto'])
    for r in rows:
        writer.writerow([
            r['tipo_doc'], r['numero_doc'], str(r['fecha_emision']), r['razon_social'] or 'N/A',
            r['descripcion'] or '', r['valor_neto'], r['iva'], r['valor_total'], 
            r['estado'], r['proyecto_codigo'] or ''
        ])
    
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=documentos.csv'}
    )


@app.route('/api/exportar-documentos-periodo')
@login_required
def exportar_documentos_periodo():
    """Exportar documentos filtrados por período"""
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    tipo_doc = request.args.get('tipo_doc', '')
    proyecto = request.args.get('proyecto', '')
    formato = request.args.get('formato', 'excel')
    
    conn = get_db()
    cur = conn.cursor()
    
    query = '''
        SELECT d.tipo_doc, d.numero_doc, d.fecha_emision, c.razon_social, 
               d.descripcion, d.valor_neto, d.iva, d.valor_total, d.estado, d.proyecto_codigo
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE 1=1
    '''
    params = []
    
    if fecha_inicio:
        query += ' AND d.fecha_emision >= %s'
        params.append(fecha_inicio)
    if fecha_fin:
        query += ' AND d.fecha_emision <= %s'
        params.append(fecha_fin)
    if tipo_doc:
        query += ' AND d.tipo_doc = %s'
        params.append(tipo_doc)
    if proyecto:
        query += ' AND d.proyecto_codigo = %s'
        params.append(proyecto)
    
    query += ' ORDER BY d.fecha_emision DESC'
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Tipo', 'N° Doc', 'Fecha', 'Cliente', 'Descripción', 'Neto', 'IVA', 'Total', 'Estado', 'Proyecto'])
    for r in rows:
        writer.writerow([
            r['tipo_doc'], r['numero_doc'], str(r['fecha_emision']), r['razon_social'] or 'N/A',
            r['descripcion'] or '', r['valor_neto'], r['iva'], r['valor_total'], 
            r['estado'], r['proyecto_codigo'] or ''
        ])
    
    filename = f'documentos_{fecha_inicio}_{fecha_fin}.csv' if fecha_inicio and fecha_fin else 'documentos_periodo.csv'
    
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@app.route('/api/exportar-clientes-cuenta/<cuenta>')
@login_required
def exportar_clientes_cuenta(cuenta):
    """Exportar clientes por cuenta corriente"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT rut, razon_social, giro, telefono, email, direccion, banco FROM clientes WHERE banco=%s AND activo=1', (cuenta,))
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['RUT', 'Razón Social', 'Giro', 'Teléfono', 'Email', 'Dirección', 'Banco'])
    for r in rows:
        writer.writerow([r['rut'], r['razon_social'], r['giro'], r['telefono'], r['email'], r['direccion'], r['banco']])
    
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=clientes_{cuenta}.csv'}
    )


@app.route('/api/ultimos-documentos/<tipo>')
@login_required
def api_ultimos_documentos(tipo):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.cliente_rut,
               d.valor_neto, d.iva, d.valor_total, d.estado, d.proyecto_codigo,
               d.motivo_nc_nd, c.razon_social as cliente_nombre
        FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE d.tipo_doc=%s ORDER BY d.id DESC LIMIT 10
    ''', (tipo,))
    docs = cur.fetchall()
    conn.close()
    
    # Formatear fechas para JSON
    for doc in docs:
        if doc.get('fecha_emision'):
            doc['fecha_emision'] = str(doc['fecha_emision'])
    
    return jsonify({'documentos': docs})


@app.route('/api/generar-boleta-rapida', methods=['POST'])
@no_consulta
def api_boleta_rapida():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        data = request.get_json()
        
        # Obtener siguiente número
        cur.execute("SELECT COALESCE(MAX(numero_doc),0)+1 as num FROM documentos WHERE tipo_doc='BOL'")
        numero = cur.fetchone()['num']
        
        cur.execute('''
            INSERT INTO documentos (numero_doc, tipo_doc, fecha_emision, cliente_rut, descripcion, valor_neto, iva, valor_total, estado, forma_pago)
            VALUES (%s, 'BOL', %s, %s, %s, %s, %s, %s, 'Pendiente', 'Contado')
        ''', (
            numero,
            data.get('fecha', datetime.now().strftime('%Y-%m-%d')),
            data.get('cliente_rut'),
            data.get('descripcion', 'Boleta rápida'),
            data.get('valor_neto', 0),
            data.get('iva', 0),
            data.get('valor_total', 0)
        ))
        conn.commit()
        return jsonify({'success': True, 'numero': numero})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
