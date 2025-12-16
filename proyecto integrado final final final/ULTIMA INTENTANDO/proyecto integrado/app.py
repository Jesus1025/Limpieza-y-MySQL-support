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


# ============================================================
# RUTAS DE PRUEBA
# ============================================================

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
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
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
    conn.close()
    return render_template('notas_credito.html', clientes=clientes)


@app.route('/notas-debito')
@login_required
def notas_debito():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rut, razon_social FROM clientes WHERE activo=1")
    clientes = cur.fetchall()
    conn.close()
    return render_template('notas_debito.html', clientes=clientes)


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
@login_required
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
@login_required
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
def api_clientes():
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
        
        # POST
        data = request.get_json() or {}
        rut = (data.get('rut') or '').strip()
        razon = (data.get('razon_social') or '').strip()
        
        if not rut or not razon:
            return jsonify({'success': False, 'error': 'RUT y Razón Social son obligatorios'}), 400
        
        if not validate_rut(rut):
            return jsonify({'success': False, 'error': 'RUT inválido'}), 400
        
        rut_n = normalize_rut(rut)
        
        # Verificar si existe
        cur.execute("SELECT id FROM clientes WHERE rut=%s", (rut_n,))
        existe = cur.fetchone()
        
        if existe:
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
                data.get('email', ''),
                data.get('direccion', ''),
                data.get('comuna', ''),
                data.get('cuenta_corriente', ''),
                data.get('banco', ''),
                data.get('observaciones', ''),
                rut_n
            ))
            msg = 'Cliente actualizado'
        else:
            cur.execute('''
                INSERT INTO clientes (rut, razon_social, giro, telefono, email, direccion, comuna, cuenta_corriente, banco, observaciones, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            ''', (
                rut_n,
                razon,
                data.get('giro', ''),
                data.get('telefono', ''),
                data.get('email', ''),
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
def api_proyectos():
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


@app.route('/api/proyectos/<codigo>', methods=['PUT', 'DELETE'])
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
# API DOCUMENTOS
# ============================================================

@app.route('/api/generar-documento', methods=['POST'])
@login_required
def api_generar_documento():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        data = request.get_json()
        cur.execute('''
            INSERT INTO documentos (numero_doc, tipo_doc, fecha_emision, cliente_rut, descripcion, valor_neto, iva, valor_total, estado, forma_pago, proyecto_codigo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente', %s, %s)
        ''', (
            data['numero_doc'], data['tipo_doc'], data['fecha_emision'],
            data['cliente_rut'], data['descripcion'],
            data['valor_neto'], data['iva'], data['valor_total'],
            data.get('forma_pago','Contado'), data.get('proyecto_codigo')
        ))
        conn.commit()
        return jsonify({'success': True})
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
        SELECT d.*, c.razon_social as cliente FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE d.estado='Pendiente' ORDER BY d.fecha_emision DESC LIMIT 10
    ''')
    docs = cur.fetchall()
    conn.close()
    return jsonify(docs)


@app.route('/api/documentos/<int:doc_id>/estado', methods=['PUT'])
@login_required
def api_doc_estado(doc_id):
    data = request.get_json() or {}
    estado = data.get('estado', '')
    
    if estado not in ['Pendiente', 'Pagado', 'Anulado']:
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
        SELECT c.rut, c.razon_social, COUNT(d.id) as cantidad, COALESCE(SUM(d.valor_total),0) as total
        FROM clientes c
        LEFT JOIN documentos d ON c.rut=d.cliente_rut AND d.estado='Pendiente'
        WHERE c.activo=1 GROUP BY c.rut, c.razon_social HAVING total > 0
    ''')
    result = cur.fetchall()
    conn.close()
    return jsonify(result)


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


@app.route('/api/ultimos-documentos/<tipo>')
@login_required
def api_ultimos_documentos(tipo):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.*, c.razon_social FROM documentos d
        LEFT JOIN clientes c ON d.cliente_rut=c.rut
        WHERE d.tipo_doc=%s ORDER BY d.id DESC LIMIT 10
    ''', (tipo,))
    docs = cur.fetchall()
    conn.close()
    return jsonify(docs)


@app.route('/api/generar-boleta-rapida', methods=['POST'])
@login_required
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
