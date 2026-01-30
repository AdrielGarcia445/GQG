import io
from datetime import datetime
from functools import wraps

import firebase_admin
import pandas as pd
from firebase_admin import credentials, firestore
from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, session, url_for)

app = Flask(__name__)

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================
# IMPORTANTE: Cambia esta clave secreta por una única y segura
app.secret_key = 'tu-clave-secreta-super-segura-cambiame-12345'

# Contraseña del sistema (cámbiala por la que prefieras)
SISTEMA_PASSWORD = 'adrielSofi04'

# ============================================================================
# INICIALIZACIÓN DE FIREBASE
# ============================================================================
# IMPORTANTE: Descarga tu archivo JSON de credenciales desde Firebase Console:
# 1. Ve a Project Settings > Service Accounts
# 2. Haz clic en "Generate New Private Key"
# 3. Guarda el archivo como 'firebase-credentials.json' en la raíz del proyecto

cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Nombre de la colección principal en Firestore
COLLECTION_NAME = 'cirugias_cardiovasculares'
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == SISTEMA_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Contraseña incorrecta')
    
    # Si ya está autenticado, redirigir al dashboard
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('authenticated', None)
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
        cirugias_ref = db.collection(COLLECTION_NAME)
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
        doc_ref = db.collection(COLLECTION_NAME).document(cirugia_id)
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
        
        # Guardar en Firestore
        doc_ref = db.collection(COLLECTION_NAME).document()
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
        doc_ref = db.collection(COLLECTION_NAME).document(cirugia_id)
        
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
        doc_ref = db.collection(COLLECTION_NAME).document(cirugia_id)
        
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
        cirugias_ref = db.collection(COLLECTION_NAME)
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
        cirugias_ref = db.collection(COLLECTION_NAME)
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
    app.run(debug=True, host='0.0.0.0', port=5000)