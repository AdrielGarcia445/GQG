import base64
import io
import json
import os
from datetime import datetime
from functools import wraps

import firebase_admin
import pandas as pd
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================
# Cargar desde variables de entorno
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-change-in-production')

# Contraseña del sistema
SISTEMA_PASSWORD = os.getenv('SISTEMA_PASSWORD')

# ============================================================================
# INICIALIZACIÓN DE FIREBASE
# ============================================================================
# Cargar credenciales desde variable de entorno (soporta JSON string o Base64)
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
firebase_credentials_base64 = os.getenv('FIREBASE_CREDENTIALS_BASE64')

if not firebase_credentials_json and not firebase_credentials_base64:
    raise ValueError(
        "Error: Ni FIREBASE_CREDENTIALS_JSON ni FIREBASE_CREDENTIALS_BASE64 están configuradas.\n"
        "Opción 1: Usa FIREBASE_CREDENTIALS_BASE64 (recomendado para producción)\n"
        "Opción 2: Usa FIREBASE_CREDENTIALS_JSON (para desarrollo local)"
    )

try:
    # Si vienen en base64, decodificar primero
    if firebase_credentials_base64:
        firebase_credentials_json = base64.b64decode(firebase_credentials_base64).decode('utf-8')
    
    firebase_credentials_dict = json.loads(firebase_credentials_json)
    cred = credentials.Certificate(firebase_credentials_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase inicializado correctamente")
except json.JSONDecodeError as e:
    raise ValueError(f"Error al parsear credenciales Firebase: {str(e)}") from e
except Exception as e:
    raise ValueError(f"Error al inicializar Firebase: {str(e)}") from e

# Nombre de las colecciones en Firestore (desde variables de entorno)
COLLECTION_NAME = os.getenv('FIREBASE_COLLECTION_NAME', 'cirugias_cardiovasculares')
USERS_COLLECTION = os.getenv('FIREBASE_USERS_COLLECTION', 'usuarios')

# ============================================================================
# FUNCIÓN AUXILIAR PARA OBTENER LA COLECCIÓN CORRECTA
# ============================================================================

def get_cirugias_collection():
    """Retorna la colección correcta según si es admin o usuario"""
    if session.get('is_admin'):
        return db.collection(COLLECTION_NAME)
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError("Usuario no autenticado")
    return db.collection(user_id)

# ============================================================================
# DECORADOR DE AUTENTICACIÓN
# ============================================================================

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# FUNCIÓN AUXILIAR PARA PROCESAR DATOS DEL FORMULARIO
# ============================================================================

def procesar_datos_formulario(data):
    """
    Procesa y limpia los datos del formulario antes de guardarlos
    Maneja arrays de checkboxes y campos vacíos
    """
    # Convertir campos numéricos vacíos a None
    campos_numericos = [
        'edad', 'peso', 'altura', 'duracion_minutos', 
        'fevi_preop', 'euroscore', 'tiempo_cec', 'tiempo_clampeo',
        'numero_puentes', 'dias_uci', 'dias_hospitalizacion', 'horas_ventilacion'
    ]
    
    for campo in campos_numericos:
        if campo in data and (data[campo] == '' or data[campo] is None):
            data[campo] = None
        elif campo in data and data[campo] != None:
            try:
                # Convertir a float o int según corresponda
                if campo in ['peso', 'altura', 'euroscore', 'horas_ventilacion']:
                    data[campo] = float(data[campo])
                else:
                    data[campo] = int(data[campo])
            except (ValueError, TypeError):
                data[campo] = None
    
    # Procesar comorbilidades (viene como array de checkboxes)
    if 'comorbilidades' in data:
        if isinstance(data['comorbilidades'], list):
            # Si ya es una lista, la dejamos así
            comorbilidades_seleccionadas = data['comorbilidades']
        else:
            # Si es un string, lo convertimos a lista
            comorbilidades_seleccionadas = [data['comorbilidades']]
    else:
        comorbilidades_seleccionadas = []
    
    # Agregar comorbilidades adicionales si existen
    if 'comorbilidades_adicionales' in data and data['comorbilidades_adicionales']:
        data['comorbilidades'] = comorbilidades_seleccionadas
        # Mantener las adicionales en campo separado
    else:
        data['comorbilidades'] = comorbilidades_seleccionadas
        data['comorbilidades_adicionales'] = ''
    
    # Limpiar campos de texto vacíos
    campos_texto = [
        'cedula', 'telefono', 'grupo_sanguineo', 'diagnostico', 
        'comorbilidades_adicionales', 'medicamentos_previos', 'alergias',
        'hora_inicio', 'hora_fin', 'procedimiento_adicional', 
        'descripcion_quirurgica', 'primer_ayudante', 'segundo_ayudante',
        'anestesiologo', 'perfusionista', 'nyha_preop', 'tipo_protesis',
        'tipo_injerto', 'estado_postoperatorio', 'complicaciones',
        'tratamiento_postop', 'fecha_alta', 'proxima_cita', 'notas'
    ]
    
    for campo in campos_texto:
        if campo in data and data[campo] == '':
            data[campo] = None
    
    return data


# ============================================================================
# RUTAS DE AUTENTICACIÓN
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validar datos
        if not email or not password:
            return render_template('register.html', error='Email y contraseña son requeridos')
        
        # Verificar si el email ya existe
        try:
            existing = list(db.collection(USERS_COLLECTION)
                          .where('email', '==', email).limit(1).stream())
            if existing:
                return render_template('register.html', error='El email ya está registrado')
        except Exception as e:
            return render_template('register.html', error=f'Error al verificar email: {str(e)}')
        
        try:
            # Crear documento de usuario
            hashed_password = generate_password_hash(password)
            user_ref = db.collection(USERS_COLLECTION).document()
            user_ref.set({
                'email': email,
                'password': hashed_password,
                'fecha_registro': datetime.now().isoformat()
            })
            
            # Iniciar sesión automáticamente
            session['authenticated'] = True
            session['is_admin'] = False
            session['user_id'] = user_ref.id
            session['email'] = email
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('register.html', error=f'Error al registrar: {str(e)}')
    
    # Si ya está autenticado, redirigir al dashboard
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Verificar si es admin
        if password == SISTEMA_PASSWORD:
            session['authenticated'] = True
            session['is_admin'] = True
            session['user_id'] = None
            session['email'] = 'admin'
            return redirect(url_for('dashboard'))
        
        # Validar datos
        if not email or not password:
            return render_template('login.html', error='Email y contraseña son requeridos')
        
        try:
            # Buscar usuario por email
            snapshot = list(db.collection(USERS_COLLECTION)
                          .where('email', '==', email).limit(1).stream())
            
            if not snapshot:
                return render_template('login.html', error='Usuario o contraseña incorrectos')
            
            user_doc = snapshot[0]
            user_data = user_doc.to_dict()
            
            # Verificar contraseña
            if not check_password_hash(user_data.get('password', ''), password):
                return render_template('login.html', error='Usuario o contraseña incorrectos')
            
            # Iniciar sesión
            session['authenticated'] = True
            session['is_admin'] = False
            session['user_id'] = user_doc.id
            session['email'] = email
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('login.html', error=f'Error al iniciar sesión: {str(e)}')
    
    # Si ya está autenticado, redirigir al dashboard
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('authenticated', None)
    session.pop('is_admin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('login'))


# ============================================================================
# RUTAS PRINCIPALES (PROTEGIDAS)
# ============================================================================

@app.route('/')
@login_required
def dashboard():
    """Dashboard principal - listado y búsqueda de cirugías"""
    return render_template('dashboard.html')


@app.route('/form')
@login_required
def form():
    """Formulario de registro/edición"""
    return render_template('form.html')


# ============================================================================
# API ENDPOINTS (PROTEGIDOS)
# ============================================================================

@app.route('/api/cirugias', methods=['GET'])
@login_required
def get_cirugias():
    """Obtener todas las cirugías"""
    try:
        cirugias_ref = get_cirugias_collection()
        docs = cirugias_ref.stream()
        
        cirugias = []
        for doc in docs:
            cirugia = doc.to_dict()
            cirugia['id'] = doc.id
            cirugias.append(cirugia)
        
        # Ordenar por fecha (más reciente primero)
        cirugias.sort(key=lambda x: x.get('fecha_cirugia', ''), reverse=True)
        
        return jsonify({'success': True, 'data': cirugias})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cirugia/<cirugia_id>', methods=['GET'])
@login_required
def get_cirugia(cirugia_id):
    """Obtener una cirugía específica por ID"""
    try:
        doc_ref = get_cirugias_collection().document(cirugia_id)
        doc = doc_ref.get()
        
        if doc.exists:
            cirugia = doc.to_dict()
            cirugia['id'] = doc.id
            return jsonify({'success': True, 'data': cirugia})
        else:
            return jsonify({'success': False, 'error': 'Cirugía no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cirugia', methods=['POST'])
@login_required
def create_cirugia():
    """Crear nueva cirugía"""
    try:
        data = request.json
        
        # Procesar datos del formulario (checkboxes, campos vacíos, etc.)
        data = procesar_datos_formulario(data)
        
        # Agregar metadata
        data['fecha_registro'] = datetime.now().isoformat()
        if not session.get('is_admin'):
            data['usuario_id'] = session['user_id']
        
        # Guardar en Firestore
        doc_ref = get_cirugias_collection().document()
        doc_ref.set(data)
        
        return jsonify({
            'success': True, 
            'message': 'Cirugía registrada exitosamente',
            'id': doc_ref.id
        })
    except Exception as e:
        print(f"Error al crear cirugía: {str(e)}")  # Log para debugging
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cirugia/<cirugia_id>', methods=['PUT'])
@login_required
def update_cirugia(cirugia_id):
    """Actualizar cirugía existente"""
    try:
        data = request.json
        
        # Procesar datos del formulario
        data = procesar_datos_formulario(data)
        
        # Agregar metadata de actualización
        data['fecha_actualizacion'] = datetime.now().isoformat()
        
        # Actualizar en Firestore
        doc_ref = get_cirugias_collection().document(cirugia_id)
        
        # Verificar que el documento existe
        if not doc_ref.get().exists:
            return jsonify({'success': False, 'error': 'Cirugía no encontrada'}), 404
        
        doc_ref.update(data)
        
        return jsonify({
            'success': True, 
            'message': 'Cirugía actualizada exitosamente'
        })
    except Exception as e:
        print(f"Error al actualizar cirugía: {str(e)}")  # Log para debugging
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cirugia/<cirugia_id>', methods=['DELETE'])
@login_required
def delete_cirugia(cirugia_id):
    """Eliminar cirugía"""
    try:
        doc_ref = get_cirugias_collection().document(cirugia_id)
        
        # Verificar que el documento existe antes de eliminar
        if not doc_ref.get().exists:
            return jsonify({'success': False, 'error': 'Cirugía no encontrada'}), 404
        
        # Eliminar el documento
        doc_ref.delete()
        
        return jsonify({
            'success': True, 
            'message': 'Cirugía eliminada exitosamente'
        })
    except Exception as e:
        print(f"Error al eliminar cirugía: {str(e)}")  # Log para debugging
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export', methods=['GET'])
@login_required
def export_excel():
    """Exportar datos a Excel"""
    try:
        cirugias_ref = get_cirugias_collection()
        docs = cirugias_ref.stream()
        
        cirugias = []
        for doc in docs:
            cirugia = doc.to_dict()
            cirugia['id'] = doc.id
            
            # Convertir array de comorbilidades a string para Excel
            if 'comorbilidades' in cirugia and isinstance(cirugia['comorbilidades'], list):
                cirugia['comorbilidades_lista'] = ', '.join(cirugia['comorbilidades'])
            
            cirugias.append(cirugia)
        
        if not cirugias:
            return jsonify({'success': False, 'error': 'No hay datos para exportar'}), 404
        
        # Crear DataFrame de pandas
        df = pd.DataFrame(cirugias)
        
        # Reordenar columnas para mejor legibilidad (opcional)
        columnas_prioritarias = [
            'id', 'fecha_cirugia', 'nombre_paciente', 'edad', 'sexo',
            'procedimiento', 'cirujano_principal', 'estado_postoperatorio'
        ]
        
        columnas_existentes = [col for col in columnas_prioritarias if col in df.columns]
        otras_columnas = [col for col in df.columns if col not in columnas_prioritarias]
        df = df[columnas_existentes + otras_columnas]
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Cirugías')
            
            # Ajustar ancho de columnas (opcional)
            worksheet = writer.sheets['Cirugías']
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'cirugias_cardiovasculares_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        print(f"Error al exportar Excel: {str(e)}")  # Log para debugging
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ENDPOINT ADICIONAL: ESTADÍSTICAS (OPCIONAL)
# ============================================================================

@app.route('/api/estadisticas', methods=['GET'])
@login_required
def get_estadisticas():
    """Obtener estadísticas generales del sistema"""
    try:
        cirugias_ref = get_cirugias_collection()
        docs = cirugias_ref.stream()
        
        total = 0
        por_procedimiento = {}
        por_estado = {}
        
        for doc in docs:
            total += 1
            data = doc.to_dict()
            
            # Contar por procedimiento
            proc = data.get('procedimiento', 'No especificado')
            por_procedimiento[proc] = por_procedimiento.get(proc, 0) + 1
            
            # Contar por estado
            estado = data.get('estado_postoperatorio', 'No especificado')
            por_estado[estado] = por_estado.get(estado, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'total_cirugias': total,
                'por_procedimiento': por_procedimiento,
                'por_estado': por_estado
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    flask_host = os.getenv('FLASK_HOST', '0.0.0.0')
    flask_port = int(os.getenv('FLASK_PORT', 5000))
    flask_debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=flask_debug, host=flask_host, port=flask_port)