# ============================================================
# TEKNETAU - Sistema de Gestión (PythonAnywhere + MySQL)
# Versión: Limpia y Funcional
# ============================================================

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, Response
import os
import re
import io
import csv
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# MySQL - REQUERIDO para PythonAnywhere
import pymysql
pymysql.install_as_MySQLdb()

# ============================================================
# CONFIGURACIÓN
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'teknetau_secretkey_2025_produccion')

# Configuración MySQL para PythonAnywhere
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'Teknetautest.mysql.pythonanywhere-services.com'),
    'user': os.environ.get('MYSQL_USER', 'Teknetautest'),
    'password': os.environ.get('MYSQL_PASSWORD', '19101810Aa'),
    'database': os.environ.get('MYSQL_DATABASE', 'Teknetautest$default'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# ============================================================
# CONEXIÓN A BASE DE DATOS
# ============================================================

def get_db_connection():
    """Obtener conexión a MySQL"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"Error conectando a MySQL: {e}")
        raise e


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalize_rut(rut: str) -> str:
    """Normaliza RUT a formato SIN puntos, CON guión (ej: 12345678-9)"""
    if not rut:
        return ''
    clean = rut.upper().replace('.', '').replace('-', '').replace(' ', '').strip()
    if len(clean) < 2:
        return ''
    cuerpo, dv = clean[:-1], clean[-1]
    if cuerpo.isdigit():
        return f"{cuerpo}-{dv}"
    return f"{cuerpo}-{dv}"


def validate_rut(rut: str) -> bool:
    """Valida RUT chileno con algoritmo módulo 11"""
    if not rut:
        return False
    
    clean = rut.upper().replace('.', '').replace('-', '').replace(' ', '').strip()
    if len(clean) < 2:
        return False
    
    cuerpo = clean[:-1]
    dv = clean[-1]
    
    if not cuerpo.isdigit():
        return False
    
    # Algoritmo módulo 11
    suma = 0
    multiplicador = 2
    for i in range(len(cuerpo) - 1, -1, -1):
        suma += int(cuerpo[i]) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_esperado = '0'
    elif dv_calculado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_calculado)
    
    return dv_esperado == dv


def validate_email(email: str) -> bool:
    """Valida formato de email"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip(), re.IGNORECASE))


def validate_telefono_chileno(telefono: str) -> bool:
    """Valida teléfono chileno (opcional)"""
    if not telefono:
        return True
    telefono = telefono.strip().replace(' ', '').replace('-', '')
    pattern = r'^(\+?56)?9[0-9]{8}$'
    return bool(re.match(pattern, telefono))


def format_telefono_chileno(telefono: str) -> str:
    """Formatea teléfono chileno"""
    if not telefono:
        return ''
    telefono = telefono.strip().replace(' ', '').replace('-', '').replace('+', '')
    if telefono.startswith('56'):
        telefono = telefono[2:]
    if len(telefono) == 9 and telefono.startswith('9'):
        return f"+56 {telefono[0]} {telefono[1:5]} {telefono[5:]}"
    return telefono


# ============================================================
# DECORADORES DE AUTENTICACIÓN
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado', 'login_required': True}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_roles):
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'No autorizado', 'login_required': True}), 401
                return redirect(url_for('login'))
            
            user_role = session.get('rol', 'usuario')
            if user_role not in required_roles:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Acceso denegado'}), 403
                flash('No tienes permiso para acceder a esta sección', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================
# RUTAS DE AUTENTICACIÓN
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, nombre, rol FROM usuarios WHERE username = %s AND activo = 1', (username,))
        user = cursor.fetchone()
        conn.close()
        
        password_valid = False
        if user:
            stored_hash = user['password_hash']
            if stored_hash.startswith('pbkdf2:') or stored_hash.startswith('scrypt:'):
                password_valid = check_password_hash(stored_hash, password)
            else:
                import hashlib
                password_valid = stored_hash == hashlib.sha256(password.encode()).hexdigest()
        
        if user and password_valid:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nombre'] = user['nombre']
            session['rol'] = user['rol'] or 'usuario'
            flash(f"¡Bienvenido {user['nombre']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))


# ============================================================
# RUTAS DE PÁGINAS PRINCIPALES
# ============================================================

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE activo = 1")
        total_clientes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM proyectos WHERE estado = 'Activo'")
        total_proyectos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM documentos WHERE estado = 'Pendiente'")
        docs_pendientes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as total FROM documentos WHERE estado = 'Pendiente'")
        deuda_total = cursor.fetchone()['total'] or 0
        
        stats = {
            'total_clientes': total_clientes,
            'total_proyectos': total_proyectos,
            'documentos_pendientes': docs_pendientes,
            'deuda_total': deuda_total
        }
        
        cursor.execute('''
            SELECT d.*, c.razon_social 
            FROM documentos d 
            LEFT JOIN clientes c ON d.cliente_rut = c.rut 
            ORDER BY d.fecha_emision DESC LIMIT 5
        ''')
        documentos = cursor.fetchall()
        
        cursor.execute("SELECT rut, razon_social FROM clientes WHERE activo = 1")
        clientes = cursor.fetchall()
        
        return render_template('index.html', stats=stats, documentos=documentos, clientes=clientes)
    except Exception as e:
        print(f"Error en index: {e}")
        stats = {'total_clientes': 0, 'total_proyectos': 0, 'documentos_pendientes': 0, 'deuda_total': 0}
        return render_template('index.html', stats=stats, documentos=[], clientes=[])
    finally:
        conn.close()


@app.route('/clientes')
@login_required
def clientes():
    bancos_chile = [
        'Banco de Chile', 'BCI', 'Scotiabank', 'BBVA', 'Santander', 'Itaú',
        'Banco del Estado', 'Banco Bice', 'Banco Security', 'Banco Falabella',
        'Banco Ripley', 'HSBC', 'Otro'
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE activo = 1 ORDER BY razon_social")
    clientes_list = cursor.fetchall()
    conn.close()
    
    return render_template('clientes.html', clientes=clientes_list, bancos=sorted(bancos_chile))


@app.route('/administracion')
@role_required('admin')
def administracion():
    return render_template('administracion.html')


@app.route('/facturas')
@login_required
def facturas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT rut, razon_social FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()
    
    cursor.execute("SELECT codigo, nombre, cliente_rut FROM proyectos WHERE estado = 'Activo'")
    proyectos = cursor.fetchall()
    
    cursor.execute("SELECT COALESCE(MAX(numero_doc), 0) as ultimo FROM documentos WHERE tipo_doc = 'FAC'")
    ultima = cursor.fetchone()['ultimo']
    
    conn.close()
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('facturas.html', clientes=clientes, proyectos=proyectos, proximo_numero=ultima + 1, today=today)


@app.route('/boletas')
@login_required
def boletas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT rut, razon_social FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()
    
    cursor.execute("SELECT codigo, nombre, cliente_rut FROM proyectos WHERE estado = 'Activo'")
    proyectos = cursor.fetchall()
    
    cursor.execute("SELECT COALESCE(MAX(numero_doc), 0) as ultimo FROM documentos WHERE tipo_doc = 'BOL'")
    ultima = cursor.fetchone()['ultimo']
    
    conn.close()
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('boletas.html', clientes=clientes, proyectos=proyectos, proximo_numero=ultima + 1, today=today)


@app.route('/proyectos')
@login_required
def proyectos():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, c.razon_social
        FROM proyectos p
        LEFT JOIN clientes c ON c.rut = p.cliente_rut
        ORDER BY p.nombre
    ''')
    proyectos_list = cursor.fetchall()
    
    cursor.execute('SELECT rut, razon_social FROM clientes WHERE activo = 1 ORDER BY razon_social')
    clientes_list = cursor.fetchall()
    
    conn.close()
    return render_template('proyectos.html', proyectos=proyectos_list, clientes=clientes_list)


@app.route('/notas-credito')
@login_required
def notas_credito():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rut, razon_social FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()
    conn.close()
    return render_template('notas_credito.html', clientes=clientes)


@app.route('/notas-debito')
@login_required
def notas_debito():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rut, razon_social FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()
    conn.close()
    return render_template('notas_debito.html', clientes=clientes)


@app.route('/reportes')
@login_required
def reportes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT codigo, nombre, estado FROM proyectos ORDER BY nombre')
    proyectos = cursor.fetchall()
    conn.close()
    return render_template('reportes.html', proyectos=proyectos)


@app.route('/reportes-completos')
@login_required
def reportes_completos():
    return redirect(url_for('reportes'))


@app.route('/cambiar-password', methods=['GET', 'POST'])
@role_required('admin')
def cambiar_password():
    if request.method == 'POST':
        password_actual = request.form.get('password_actual')
        nuevo_password = request.form.get('nuevo_password')
        confirmar_password = request.form.get('confirmar_password')

        if nuevo_password != confirmar_password:
            flash('La nueva contraseña no coincide con la confirmación.', 'error')
            return redirect(url_for('cambiar_password'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM usuarios WHERE id = %s', (session['user_id'],))
        row = cursor.fetchone()
        password_hash_actual = row['password_hash'] if row else None

        password_valid = False
        if password_hash_actual:
            if password_hash_actual.startswith('pbkdf2:') or password_hash_actual.startswith('scrypt:'):
                password_valid = check_password_hash(password_hash_actual, password_actual)
            else:
                import hashlib
                password_valid = password_hash_actual == hashlib.sha256(password_actual.encode()).hexdigest()
        
        if not password_valid:
            conn.close()
            flash('La contraseña actual es incorrecta.', 'error')
            return redirect(url_for('cambiar_password'))

        nuevo_hash = generate_password_hash(nuevo_password, method='pbkdf2:sha256')
        cursor.execute('UPDATE usuarios SET password_hash = %s WHERE id = %s', (nuevo_hash, session['user_id']))
        conn.commit()
        conn.close()

        flash('Contraseña actualizada correctamente.', 'success')
        return redirect(url_for('index'))

    return render_template('cambiar_password.html')


# ============================================================
# API DE CLIENTES (PRINCIPAL)
# ============================================================

@app.route('/api/clientes', methods=['GET', 'POST', 'DELETE'])
@app.route('/api/clientes-dev', methods=['GET', 'POST', 'DELETE'])
@app.route('/api-dev/clientes', methods=['GET', 'POST', 'DELETE'])
def api_clientes():
    """API unificada de clientes"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # GET - Listar clientes
        if request.method == 'GET':
            estado = request.args.get('estado', '').lower()
            if estado == 'activo':
                cursor.execute("SELECT * FROM clientes WHERE activo = 1 ORDER BY razon_social")
            elif estado == 'inactivo':
                cursor.execute("SELECT * FROM clientes WHERE activo = 0 ORDER BY razon_social")
            else:
                cursor.execute("SELECT * FROM clientes ORDER BY razon_social")
            return jsonify(cursor.fetchall())

        # DELETE - Desactivar cliente
        if request.method == 'DELETE':
            rut = request.args.get('rut')
            if not rut:
                return jsonify({'success': False, 'error': 'RUT requerido'}), 400
            rut_norm = normalize_rut(rut)
            cursor.execute('UPDATE clientes SET activo = 0 WHERE rut = %s', (rut_norm,))
            conn.commit()
            return jsonify({'success': cursor.rowcount > 0})

        # POST - Crear/Actualizar cliente
        data = request.get_json() or {}
        rut = (data.get('rut') or '').strip()
        razon_social = (data.get('razon_social') or '').strip()
        email = (data.get('email') or '').strip()

        # Validaciones
        if not rut or not razon_social:
            return jsonify({'success': False, 'error': 'RUT y razón social son obligatorios'}), 400

        if not validate_rut(rut):
            return jsonify({'success': False, 'error': 'RUT inválido. Verifique el dígito verificador'}), 400

        if not email or not validate_email(email):
            return jsonify({'success': False, 'error': 'Debe ingresar un correo electrónico válido'}), 400

        telefono = (data.get('telefono') or '').strip()
        if telefono and not validate_telefono_chileno(telefono):
            return jsonify({'success': False, 'error': 'Formato de teléfono inválido. Use: +56 9 XXXX XXXX'}), 400

        # Normalizar datos
        rut_norm = normalize_rut(rut)
        email_norm = email.lower()
        telefono_fmt = format_telefono_chileno(telefono)
        giro = (data.get('giro') or '').strip()
        direccion = (data.get('direccion') or '').strip()
        comuna = (data.get('comuna') or '').strip()
        banco = (data.get('banco') or '').strip()
        cuenta_corriente = (data.get('cuenta_corriente') or '').strip()
        observaciones = (data.get('observaciones') or '').strip()

        # Verificar si existe
        cursor.execute("SELECT id FROM clientes WHERE rut = %s", (rut_norm,))
        existente = cursor.fetchone()

        if existente:
            # Actualizar
            cursor.execute('''
                UPDATE clientes
                SET razon_social = %s, giro = %s, telefono = %s, email = %s, 
                    direccion = %s, comuna = %s, cuenta_corriente = %s, banco = %s, 
                    observaciones = %s, activo = 1
                WHERE rut = %s
            ''', (razon_social, giro, telefono_fmt, email_norm, direccion, comuna, 
                  cuenta_corriente, banco, observaciones, rut_norm))
            mensaje = 'Cliente actualizado correctamente'
        else:
            # Insertar
            cursor.execute('''
                INSERT INTO clientes (rut, razon_social, giro, telefono, email, 
                                     direccion, comuna, cuenta_corriente, banco, observaciones, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            ''', (rut_norm, razon_social, giro, telefono_fmt, email_norm, 
                  direccion, comuna, cuenta_corriente, banco, observaciones))
            mensaje = 'Cliente creado correctamente'

        conn.commit()
        return jsonify({'success': True, 'message': mensaje})

    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        print(f"Error en api_clientes: {error_msg}")
        
        if 'Duplicate entry' in error_msg:
            return jsonify({'success': False, 'error': 'El RUT ya existe en el sistema'}), 400
        return jsonify({'success': False, 'error': f'Error: {error_msg}'}), 500
    finally:
        conn.close()


@app.route('/api/clientes/<rut>', methods=['GET', 'PUT'])
@app.route('/api/clientes-dev/<rut>', methods=['GET', 'PUT'])
def api_clientes_detalle(rut):
    """Obtener o actualizar un cliente específico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        rut_norm = normalize_rut(rut)
        
        if request.method == 'GET':
            cursor.execute("SELECT * FROM clientes WHERE rut = %s", (rut_norm,))
            cliente = cursor.fetchone()
            
            if not cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 404
            
            return jsonify(cliente)
            
        elif request.method == 'PUT':
            data = request.get_json() or {}
            razon_social = (data.get('razon_social') or '').strip()
            email = (data.get('email') or '').strip()
            telefono = (data.get('telefono') or '').strip()

            if not razon_social:
                return jsonify({'success': False, 'error': 'La razón social es obligatoria'}), 400
            
            if not email or not validate_email(email):
                return jsonify({'success': False, 'error': 'Email inválido'}), 400
            
            if telefono and not validate_telefono_chileno(telefono):
                return jsonify({'success': False, 'error': 'Teléfono inválido'}), 400

            cursor.execute('''
                UPDATE clientes
                SET razon_social = %s, giro = %s, telefono = %s, email = %s, 
                    direccion = %s, comuna = %s, cuenta_corriente = %s, banco = %s, 
                    observaciones = %s
                WHERE rut = %s
            ''', (
                razon_social,
                (data.get('giro') or '').strip(),
                format_telefono_chileno(telefono),
                email.lower(),
                (data.get('direccion') or '').strip(),
                (data.get('comuna') or '').strip(),
                (data.get('cuenta_corriente') or '').strip(),
                (data.get('banco') or '').strip(),
                (data.get('observaciones') or '').strip(),
                rut_norm
            ))
            conn.commit()
            
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Cliente actualizado'})
            else:
                return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
                
    except Exception as e:
        print(f"Error en api_clientes_detalle: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ============================================================
# API DE DOCUMENTOS
# ============================================================

@app.route('/api/generar-documento', methods=['POST'])
@login_required
def api_generar_documento():
    data = request.get_json()
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documentos (numero_doc, tipo_doc, fecha_emision, cliente_rut, descripcion, 
                                   valor_neto, iva, valor_total, estado, forma_pago, proyecto_codigo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente', %s, %s)
        ''', (
            data['numero_doc'],
            data['tipo_doc'],
            data['fecha_emision'],
            data['cliente_rut'],
            data['descripcion'],
            data['valor_neto'],
            data['iva'],
            data['valor_total'],
            data.get('forma_pago', 'Contado'),
            data.get('proyecto_codigo')
        ))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Documento generado exitosamente'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/documentos-pendientes')
@login_required
def api_documentos_pendientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.valor_total, 
                   d.estado, c.razon_social as cliente
            FROM documentos d
            LEFT JOIN clientes c ON d.cliente_rut = c.rut
            WHERE d.estado = 'Pendiente'
            ORDER BY d.fecha_emision DESC
            LIMIT 10
        ''')
        return jsonify(cursor.fetchall())
    finally:
        conn.close()


@app.route('/api/documentos/<int:doc_id>/estado', methods=['PUT'])
@login_required
def api_documento_cambiar_estado(doc_id):
    data = request.get_json() or {}
    nuevo_estado = data.get('estado', '').strip()
    
    if nuevo_estado not in ['Pendiente', 'Pagado', 'Anulado', 'Aplicada']:
        return jsonify({'success': False, 'error': 'Estado inválido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE documentos SET estado = %s WHERE id = %s', (nuevo_estado, doc_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Documento no encontrado'}), 404
    finally:
        conn.close()


@app.route('/api/ultimos-documentos/<tipo_doc>')
@login_required
def api_ultimos_documentos(tipo_doc):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.valor_total, 
                   d.estado, d.proyecto_codigo, c.razon_social as cliente_nombre
            FROM documentos d
            LEFT JOIN clientes c ON d.cliente_rut = c.rut
            WHERE d.tipo_doc = %s
            ORDER BY d.fecha_emision DESC, d.id DESC
            LIMIT 20
        ''', (tipo_doc,))
        
        return jsonify({'documentos': cursor.fetchall()})
    finally:
        conn.close()


@app.route('/api/buscar-documentos')
@login_required
def api_buscar_documentos():
    tipo_doc = request.args.get('tipo_doc', '')
    estado = request.args.get('estado', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    proyecto = request.args.get('proyecto', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.cliente_rut,
                   d.descripcion, d.valor_neto, d.iva, d.valor_total, d.estado,
                   d.proyecto_codigo, c.razon_social
            FROM documentos d
            LEFT JOIN clientes c ON d.cliente_rut = c.rut
            WHERE 1=1
        '''
        params = []
        
        if tipo_doc:
            query += ' AND d.tipo_doc = %s'
            params.append(tipo_doc)
        if estado:
            query += ' AND d.estado = %s'
            params.append(estado)
        if fecha_desde:
            query += ' AND d.fecha_emision >= %s'
            params.append(fecha_desde)
        if fecha_hasta:
            query += ' AND d.fecha_emision <= %s'
            params.append(fecha_hasta)
        if proyecto:
            query += ' AND d.proyecto_codigo = %s'
            params.append(proyecto)
        
        query += ' ORDER BY d.fecha_emision DESC LIMIT 500'
        
        cursor.execute(query, params)
        return jsonify({'documentos': cursor.fetchall()})
    finally:
        conn.close()


# ============================================================
# API DE PROYECTOS
# ============================================================

@app.route('/api/proyectos', methods=['GET', 'POST'])
@login_required
def api_proyectos():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if request.method == 'GET':
            cursor.execute('''
                SELECT p.*, c.razon_social
                FROM proyectos p
                LEFT JOIN clientes c ON c.rut = p.cliente_rut
                ORDER BY p.id DESC
            ''')
            return jsonify(cursor.fetchall())

        # POST
        data = request.get_json() or {}
        codigo = (data.get('codigo') or '').strip()
        nombre = (data.get('nombre') or '').strip()
        cliente_rut = (data.get('cliente_rut') or '').strip()
        fecha_inicio = (data.get('fecha_inicio') or '').strip()

        if not codigo or not nombre or not cliente_rut or not fecha_inicio:
            return jsonify({'success': False, 'error': 'Código, nombre, cliente y fecha son obligatorios'}), 400

        cliente_rut_norm = normalize_rut(cliente_rut)
        
        try:
            presupuesto = float(data.get('presupuesto') or 0)
        except ValueError:
            return jsonify({'success': False, 'error': 'El presupuesto debe ser numérico'}), 400

        fecha_termino = data.get('fecha_termino') or None
        estado = (data.get('estado') or 'Activo').strip()

        cursor.execute('SELECT id FROM proyectos WHERE codigo = %s', (codigo,))
        existente = cursor.fetchone()

        if existente:
            cursor.execute('''
                UPDATE proyectos
                SET nombre = %s, descripcion = %s, cliente_rut = %s, presupuesto = %s, 
                    fecha_inicio = %s, fecha_termino = %s, estado = %s
                WHERE codigo = %s
            ''', (nombre, data.get('descripcion'), cliente_rut_norm, presupuesto, 
                  fecha_inicio, fecha_termino, estado, codigo))
        else:
            cursor.execute('''
                INSERT INTO proyectos (codigo, nombre, descripcion, cliente_rut, presupuesto, 
                                      fecha_inicio, fecha_termino, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (codigo, nombre, data.get('descripcion'), cliente_rut_norm, presupuesto, 
                  fecha_inicio, fecha_termino, estado))

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/proyectos/<codigo>', methods=['PUT', 'DELETE'])
@login_required
def api_proyectos_update_delete(codigo):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'DELETE':
            cursor.execute('DELETE FROM proyectos WHERE codigo = %s', (codigo,))
            conn.commit()
            return jsonify({'success': cursor.rowcount > 0})
        
        # PUT
        data = request.get_json() or {}
        cursor.execute('''
            UPDATE proyectos
            SET nombre = %s, descripcion = %s, cliente_rut = %s, presupuesto = %s, 
                fecha_inicio = %s, fecha_termino = %s, estado = %s
            WHERE codigo = %s
        ''', (
            data.get('nombre'),
            data.get('descripcion'),
            normalize_rut(data.get('cliente_rut', '')),
            float(data.get('presupuesto') or 0),
            data.get('fecha_inicio'),
            data.get('fecha_termino'),
            data.get('estado', 'Activo'),
            codigo
        ))
        conn.commit()
        return jsonify({'success': cursor.rowcount > 0})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/proyecto/<codigo>/progreso')
@login_required
def api_proyecto_progreso(codigo):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT p.*, c.razon_social 
            FROM proyectos p
            LEFT JOIN clientes c ON p.cliente_rut = c.rut
            WHERE p.codigo = %s
        ''', (codigo,))
        proyecto = cursor.fetchone()
        
        if not proyecto:
            return jsonify({'error': 'Proyecto no encontrado'}), 404
        
        cursor.execute('''
            SELECT * FROM documentos WHERE proyecto_codigo = %s ORDER BY fecha_emision DESC
        ''', (codigo,))
        documentos = cursor.fetchall()
        
        presupuesto = proyecto['presupuesto'] or 0
        
        total_facturado = sum(
            d['valor_total'] or 0 
            for d in documentos 
            if d['tipo_doc'] in ('FAC', 'BOL') and d['estado'] != 'Anulado'
        )
        
        total_pagado = sum(
            d['valor_total'] or 0 
            for d in documentos 
            if d['tipo_doc'] in ('FAC', 'BOL') and d['estado'] == 'Pagado'
        )
        
        total_pendiente = max(0, total_facturado - total_pagado)
        
        if presupuesto > 0:
            porcentaje = min(100, (total_pagado / presupuesto) * 100)
        elif total_facturado > 0:
            porcentaje = (total_pagado / total_facturado) * 100
        else:
            porcentaje = 0
        
        return jsonify({
            'proyecto': {
                'codigo': proyecto['codigo'],
                'nombre': proyecto['nombre'],
                'cliente': proyecto['razon_social'],
                'presupuesto': presupuesto,
                'estado': proyecto['estado']
            },
            'progreso': {
                'total_facturado': total_facturado,
                'total_pagado': total_pagado,
                'total_pendiente': total_pendiente,
                'porcentaje_pagado': round(porcentaje, 2)
            },
            'documentos': documentos,
            'cantidad_documentos': len(documentos)
        })
    finally:
        conn.close()


@app.route('/api/proyecto/<codigo>/documentos')
@login_required
def api_proyecto_documentos(codigo):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT d.*, c.razon_social as cliente_nombre
            FROM documentos d
            LEFT JOIN clientes c ON d.cliente_rut = c.rut
            WHERE d.proyecto_codigo = %s
            ORDER BY d.fecha_emision DESC
        ''', (codigo,))
        
        return jsonify(cursor.fetchall())
    finally:
        conn.close()


# ============================================================
# API DE REPORTES
# ============================================================

@app.route('/api/reporte-deudas')
@login_required
def api_reporte_deudas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT c.rut, c.razon_social, COUNT(d.id) as cantidad, 
                   COALESCE(SUM(d.valor_total), 0) as total
            FROM clientes c
            LEFT JOIN documentos d ON c.rut = d.cliente_rut AND d.estado = 'Pendiente'
            WHERE c.activo = 1
            GROUP BY c.rut, c.razon_social
            HAVING total > 0
        ''')
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/reporte-ventas-mensual')
@login_required
def api_reporte_ventas_mensual():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT DATE_FORMAT(fecha_emision, '%%Y-%%m') as mes, tipo_doc, 
                   COUNT(*) as cantidad, SUM(valor_total) as total
            FROM documentos 
            WHERE tipo_doc IN ('FAC', 'BOL') AND estado != 'Anulado'
            GROUP BY mes, tipo_doc
            ORDER BY mes DESC
        ''')
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/reporte-top-clientes')
@login_required
def api_reporte_top_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT c.razon_social, c.rut, COUNT(d.id) as documentos, 
                   COALESCE(SUM(d.valor_total), 0) as total
            FROM clientes c
            LEFT JOIN documentos d ON c.rut = d.cliente_rut 
            WHERE d.estado != 'Anulado' AND d.tipo_doc IN ('FAC', 'BOL')
            GROUP BY c.rut, c.razon_social
            ORDER BY total DESC
            LIMIT 10
        ''')
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/reporte-resumen')
@login_required
def api_reporte_resumen():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as t FROM documentos WHERE tipo_doc IN ('FAC', 'BOL')")
        total_facturado = cursor.fetchone()['t']
        
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as t FROM documentos WHERE tipo_doc IN ('FAC', 'BOL') AND estado = 'Pagado'")
        total_pagado = cursor.fetchone()['t']
        
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as t FROM documentos WHERE tipo_doc IN ('FAC', 'BOL') AND estado = 'Pendiente'")
        total_pendiente = cursor.fetchone()['t']
        
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as t FROM documentos WHERE tipo_doc = 'NC'")
        total_nc = cursor.fetchone()['t']
        
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) as t FROM documentos WHERE tipo_doc = 'ND'")
        total_nd = cursor.fetchone()['t']
        
        cursor.execute('SELECT COUNT(*) as c FROM documentos WHERE estado = "Pagado"')
        count_pagados = cursor.fetchone()['c']
        
        cursor.execute('SELECT COUNT(*) as c FROM documentos WHERE estado = "Pendiente"')
        count_pendientes = cursor.fetchone()['c']
        
        cursor.execute('SELECT COUNT(*) as c FROM documentos WHERE tipo_doc = "NC"')
        count_nc = cursor.fetchone()['c']
        
        cursor.execute('SELECT COUNT(*) as c FROM documentos WHERE estado = "Anulado"')
        count_anulados = cursor.fetchone()['c']
        
        cursor.execute('SELECT COUNT(*) as c FROM documentos')
        total_documentos = cursor.fetchone()['c']
        
        return jsonify({
            'total_facturado': total_facturado,
            'total_pagado': total_pagado,
            'total_pendiente': total_pendiente,
            'total_nc': total_nc,
            'total_nd': total_nd,
            'count_pagados': count_pagados,
            'count_pendientes': count_pendientes,
            'count_nc': count_nc,
            'count_anulados': count_anulados,
            'total_documentos': total_documentos
        })
    finally:
        conn.close()


@app.route('/api/reporte-nc-nd')
@login_required
def api_reporte_nc_nd():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT d.id, d.numero_doc, d.tipo_doc, d.fecha_emision, d.cliente_rut,
                   d.descripcion, d.valor_neto, d.iva, d.valor_total, d.estado,
                   c.razon_social, c.email as cliente_email
            FROM documentos d
            LEFT JOIN clientes c ON d.cliente_rut = c.rut
            WHERE d.tipo_doc IN ('NC', 'ND')
            ORDER BY d.fecha_emision DESC
        ''')
        return jsonify(cursor.fetchall())
    finally:
        conn.close()


# ============================================================
# API DE ADMINISTRACIÓN
# ============================================================

@app.route('/api/cambiar-password', methods=['POST'])
@login_required
def api_cambiar_password():
    data = request.get_json() or {}
    password_actual = data.get('password_actual', '').strip()
    password_nueva = data.get('password_nueva', '').strip()
    
    if not password_actual or not password_nueva:
        return jsonify({'success': False, 'error': 'Contraseñas requeridas'}), 400
    
    if len(password_nueva) < 8:
        return jsonify({'success': False, 'error': 'Mínimo 8 caracteres'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT password_hash FROM usuarios WHERE id = %s", (session['user_id'],))
        usuario = cursor.fetchone()
        
        if not usuario or not check_password_hash(usuario['password_hash'], password_actual):
            return jsonify({'success': False, 'error': 'Contraseña actual incorrecta'}), 401
        
        nueva_hash = generate_password_hash(password_nueva, method='pbkdf2:sha256')
        cursor.execute("UPDATE usuarios SET password_hash = %s WHERE id = %s", (nueva_hash, session['user_id']))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Contraseña actualizada'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/usuarios-dev', methods=['GET', 'POST', 'DELETE'])
@role_required('admin')
def api_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'GET':
            cursor.execute("SELECT id, username, nombre, email, rol, activo, fecha_creacion FROM usuarios ORDER BY username")
            return jsonify(cursor.fetchall())
        
        if request.method == 'DELETE':
            usuario_id = request.args.get('id')
            if not usuario_id:
                return jsonify({'success': False, 'error': 'ID requerido'}), 400
            
            if int(usuario_id) == session.get('user_id'):
                return jsonify({'success': False, 'error': 'No puedes eliminar tu propio usuario'}), 403
            
            cursor.execute('DELETE FROM usuarios WHERE id = %s', (usuario_id,))
            conn.commit()
            return jsonify({'success': cursor.rowcount > 0})
        
        # POST
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        nombre = (data.get('nombre') or '').strip()
        email = (data.get('email') or '').strip()
        rol = (data.get('rol') or 'usuario').strip()
        password = (data.get('password') or '').strip()
        usuario_id = data.get('id')
        
        if not username or not nombre or not email:
            return jsonify({'success': False, 'error': 'Username, nombre y email son obligatorios'}), 400
        
        if not validate_email(email):
            return jsonify({'success': False, 'error': 'Email inválido'}), 400
        
        if usuario_id:
            # Actualizar
            if password:
                if len(password) < 8:
                    return jsonify({'success': False, 'error': 'Contraseña debe tener mínimo 8 caracteres'}), 400
                password_hash = generate_password_hash(password, method='pbkdf2:sha256')
                cursor.execute('''
                    UPDATE usuarios SET nombre = %s, email = %s, rol = %s, password_hash = %s WHERE id = %s
                ''', (nombre, email, rol, password_hash, usuario_id))
            else:
                cursor.execute('''
                    UPDATE usuarios SET nombre = %s, email = %s, rol = %s WHERE id = %s
                ''', (nombre, email, rol, usuario_id))
        else:
            # Crear
            if not password or len(password) < 8:
                return jsonify({'success': False, 'error': 'Contraseña requerida (mínimo 8 caracteres)'}), 400
            
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'success': False, 'error': 'El usuario ya existe'}), 400
            
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute('''
                INSERT INTO usuarios (username, nombre, email, rol, password_hash, activo)
                VALUES (%s, %s, %s, %s, %s, 1)
            ''', (username, nombre, email, rol, password_hash))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ============================================================
# EXPORTACIÓN CSV
# ============================================================

@app.route('/api/exportar-clientes-csv')
@login_required
def api_exportar_clientes_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT rut, razon_social, giro, telefono, email, direccion, comuna, banco FROM clientes WHERE activo = 1 ORDER BY razon_social')
        rows = cursor.fetchall()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['RUT', 'Razón Social', 'Giro', 'Teléfono', 'Email', 'Dirección', 'Comuna', 'Banco'])
        
        for row in rows:
            writer.writerow([row['rut'], row['razon_social'], row['giro'], row['telefono'], 
                           row['email'], row['direccion'], row['comuna'], row['banco']])
        
        csv_content = '\ufeff' + output.getvalue()
        
        return Response(
            csv_content,
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename=clientes.csv'}
        )
    finally:
        conn.close()


@app.route('/api/exportar-proyectos-csv')
@login_required
def api_exportar_proyectos_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT p.codigo, p.nombre, p.descripcion, c.razon_social, p.presupuesto, 
                   p.fecha_inicio, p.fecha_termino, p.estado
            FROM proyectos p
            LEFT JOIN clientes c ON p.cliente_rut = c.rut
        ''')
        rows = cursor.fetchall()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Código', 'Nombre', 'Descripción', 'Cliente', 'Presupuesto', 'Fecha Inicio', 'Fecha Término', 'Estado'])
        
        for row in rows:
            writer.writerow([row['codigo'], row['nombre'], row['descripcion'], row['razon_social'], 
                           row['presupuesto'], row['fecha_inicio'], row['fecha_termino'], row['estado']])
        
        csv_content = '\ufeff' + output.getvalue()
        
        return Response(
            csv_content,
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename=proyectos.csv'}
        )
    finally:
        conn.close()


@app.route('/api/exportar-deudas-excel')
@login_required
def api_exportar_deudas_excel():
    try:
        import openpyxl
        from openpyxl.utils import get_column_letter
    except ImportError:
        return jsonify({'error': 'openpyxl no instalado'}), 500
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT d.numero_doc, d.tipo_doc, d.fecha_emision, c.razon_social, c.rut,
                   d.valor_total, d.proyecto_codigo
            FROM documentos d
            LEFT JOIN clientes c ON d.cliente_rut = c.rut
            WHERE d.estado = 'Pendiente' AND d.tipo_doc IN ('FAC', 'BOL', 'ND')
            ORDER BY c.razon_social, d.fecha_emision
        ''')
        rows = cursor.fetchall()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Deudas Pendientes"
        
        headers = ['N° Doc', 'Tipo', 'Fecha', 'Cliente', 'RUT', 'Monto', 'Proyecto']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        for row_num, row in enumerate(rows, 2):
            ws.cell(row=row_num, column=1, value=row['numero_doc'])
            ws.cell(row=row_num, column=2, value=row['tipo_doc'])
            ws.cell(row=row_num, column=3, value=row['fecha_emision'])
            ws.cell(row=row_num, column=4, value=row['razon_social'])
            ws.cell(row=row_num, column=5, value=row['rut'])
            ws.cell(row=row_num, column=6, value=row['valor_total'])
            ws.cell(row=row_num, column=7, value=row['proyecto_codigo'])
        
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 15
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='reporte_deudas.xlsx'
        )
    finally:
        conn.close()


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == '__main__':
    print("Iniciando servidor de desarrollo...")
    app.run(debug=True, port=5000)
