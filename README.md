# 🫀 G.Q.G - Gestor Quirúrgico García

Sistema de registro de cirugías cardiovasculares desarrollado en Flask con Firebase como base de datos NoSQL.

## 📋 Características

- **Sistema cerrado** para un solo usuario (sin autenticación)
- **Base de datos NoSQL** con Firebase Firestore
- **Interfaz web simple** con solo 2 templates
- **Dashboard** completo con búsqueda, filtrado y estadísticas
- **Formulario detallado** para datos cardiovasculares
- **Exportación a Excel** con pandas
- **Datos multidisciplinarios**: paciente, procedimiento, equipo quirúrgico, postoperatorio, seguimiento

## 🚀 Instalación

### 1. Requisitos Previos

- Python 3.8 o superior
- Cuenta de Google/Firebase

### 2. Clonar/Descargar el proyecto

```bash
cd gqg_project
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Firebase

#### Paso 1: Crear proyecto en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Haz clic en "Agregar proyecto"
3. Nombra tu proyecto (ej: "gqg-garcia")
4. Sigue los pasos de configuración

#### Paso 2: Crear base de datos Firestore

1. En la consola de Firebase, ve a **Firestore Database**
2. Haz clic en "Crear base de datos"
3. Selecciona modo de **producción** o **prueba** (para desarrollo, usa modo prueba)
4. Elige la ubicación más cercana (ej: `us-east1`)

#### Paso 3: Descargar credenciales

1. Ve a **Configuración del proyecto** (ícono de engranaje)
2. Selecciona la pestaña **Cuentas de servicio**
3. Haz clic en **Generar nueva clave privada**
4. Se descargará un archivo JSON
5. **Renombra el archivo a `firebase-credentials.json`**
6. **Coloca el archivo en la raíz del proyecto** (mismo nivel que `app.py`)

#### Estructura esperada:
```
gqg_project/
├── app.py
├── firebase-credentials.json  ← AQUÍ
├── requirements.txt
└── templates/
    ├── dashboard.html
    └── form.html
```

#### Paso 4: Configurar reglas de seguridad (opcional)

En Firestore Database > Reglas, puedes usar:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;  // Para desarrollo sin autenticación
    }
  }
}
```

**IMPORTANTE**: Estas reglas son solo para desarrollo local. En producción deberías implementar autenticación.

## ▶️ Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 📁 Estructura del Proyecto

```
gqg_project/
├── app.py                      # Aplicación Flask principal
├── firebase-credentials.json   # Credenciales de Firebase (NO subir a Git)
├── requirements.txt            # Dependencias Python
├── README.md                   # Esta documentación
└── templates/
    ├── dashboard.html          # Vista principal (listado, búsqueda, filtros)
    └── form.html               # Formulario de registro/edición
```

## 🗄️ Nombre de la Colección en Firestore

El sistema utiliza la colección: **`cirugias_cardiovasculares`**

Puedes cambiar este nombre editando la variable `COLLECTION_NAME` en `app.py`:

```python
COLLECTION_NAME = 'cirugias_cardiovasculares'  # Cambia aquí si necesitas otro nombre
```

## 📊 Datos Registrados

### Datos del Paciente
- Nombre completo, edad, sexo, cédula
- Datos físicos: peso, altura, grupo sanguíneo
- Contacto: teléfono

### Antecedentes Médicos
- Diagnóstico principal
- Comorbilidades
- Medicamentos previos
- Alergias

### Datos de la Cirugía
- Fecha y hora (inicio/fin/duración)
- Procedimiento cardiovascular
- Descripción quirúrgica
- Equipo: cirujano, ayudante, anestesiólogo, perfusionista

### Datos Cardiovasculares Específicos
- FEVI preoperatoria
- Clase funcional NYHA
- Riesgo Euroscore II
- Tiempo de circulación extracorpórea
- Tiempo de clampeo aórtico
- Número de puentes
- Tipo de prótesis/injerto

### Postoperatorio
- Estado postoperatorio
- Días en UCI, hospitalización, ventilación mecánica
- Complicaciones
- Tratamiento postoperatorio

### Seguimiento
- Fecha de alta
- Próxima cita
- Notas adicionales

## 🔧 Funcionalidades

### Dashboard
- ✅ Listado completo de cirugías
- ✅ Búsqueda en tiempo real
- ✅ Filtros por fecha (desde/hasta)
- ✅ Filtro por estado postoperatorio
- ✅ Estadísticas: total cirugías, cirugías del mes, pacientes únicos
- ✅ Editar cirugías
- ✅ Eliminar cirugías
- ✅ Exportar a Excel

### Formulario
- ✅ Registro de nueva cirugía
- ✅ Edición de cirugía existente
- ✅ Validación de campos requeridos
- ✅ Cálculo automático de duración
- ✅ Campos específicos cardiovasculares

## 📤 Exportar a Excel

1. En el dashboard, haz clic en **"📊 Exportar Excel"**
2. Se descargará un archivo `.xlsx` con todos los datos
3. El archivo incluye todas las columnas con timestamp en el nombre

## ⚠️ Seguridad

Este MVP es para **un solo usuario** y **no incluye autenticación**.

Para uso en producción:
- Implementa autenticación (Firebase Auth, Flask-Login, etc.)
- Configura reglas de seguridad en Firestore
- Usa variables de entorno para credenciales
- Agrega validación de entrada adicional
- Implementa logging de auditoría

## 🔒 .gitignore recomendado

Crea un archivo `.gitignore` con:

```
firebase-credentials.json
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
*.log
.DS_Store
```

## 🐛 Solución de Problemas

### Error: "firebase-credentials.json not found"
- Asegúrate de haber descargado las credenciales de Firebase
- Verifica que el archivo esté en la raíz del proyecto
- Verifica que el nombre sea exactamente `firebase-credentials.json`

### Error: "Permission denied" en Firestore
- Verifica las reglas de seguridad en Firestore
- Para desarrollo, permite lectura/escritura a todos

### La aplicación no inicia
- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
- Verifica que Python 3.8+ esté instalado: `python --version`

## 📝 Notas de Desarrollo

- Firebase Firestore usa documentos y colecciones (NoSQL)
- Cada cirugía es un documento con ID único
- Los datos se guardan como diccionarios JSON
- Pandas convierte los documentos a DataFrame para Excel

## 🎯 Próximas Mejoras (opcional)

- [ ] Autenticación de usuario
- [ ] Múltiples usuarios/médicos
- [ ] Reportes estadísticos avanzados
- [ ] Gráficos de tendencias
- [ ] Backup automático
- [ ] Notificaciones de seguimiento
- [ ] Adjuntar archivos (imágenes, PDFs)
- [ ] Impresión de reportes

## 👨‍⚕️ Autor

**Gestor Quirúrgico García (G.Q.G)**  
Sistema de registro cardiovascular profesional

---

**Versión**: 1.0.0  
**Licencia**: MIT
