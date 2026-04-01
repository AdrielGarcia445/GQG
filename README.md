# 🫀 G.Q.G - Gestor Quirúrgico García

Sistema profesional de registro de cirugías cardiovasculares desarrollado en Flask con Firebase como base de datos NoSQL.

## 📋 Características Principales

- **🔐 Sistema de Autenticación** completo con login/registro de usuarios
- **👥 Multi-usuario** - Cada usuario tiene sus propios registros de cirugías
- **🔑 Acceso Admin** - Contraseña especial para acceso administrativo
- **📊 Base de datos NoSQL** con Firebase Firestore
- **💾 Dashboard profesional** con búsqueda, filtros avanzados y estadísticas
- **📋 Formulario completo** para datos cardiovasculares detallados
- **📥 Exportación a Excel** con formato profesional
- **📝 Logging de auditoría** para intentos de acceso
- **🔓 Control de sesiones** con logout seguro
- **👁️ Interfaz responsive** adaptada a móviles y desktop

## 🚀 Instalación Rápida

### 1. Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- ✅ Firebase: Ya está pre-configurado en el servidor (no necesitas crear nada)

### 2. Clonar o descargar el proyecto

```bash
git clone https://github.com/tu-usuario/gqg.git
cd gqg
```

### 3. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv gqg-venv
gqg-venv\Scripts\activate

# macOS/Linux
python3 -m venv gqg-venv
source gqg-venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Firebase

#### ✅ Firebase ya está preconfigrado en el servidor

La conexión a Firebase Firestore ya está configurada en el servidor. No necesitas:
- ❌ Crear un nuevo proyecto en Firebase
- ❌ Descargar credenciales JSON
- ❌ Configurar reglas de Firestore

Solo necesitas:
- ✅ Usar el entorno existente
- ✅ Configurar las variables de entorno locales (paso siguiente)

### 6. Configurar variables de entorno (LOCAL)

Crea un archivo `.env` en la raíz del proyecto con tus valores de desarrollo local:

```env
# Seguridad - usa valores seguros para desarrollo local
FLASK_SECRET_KEY=cambiar-por-clave-aleatoria-fuerte
SISTEMA_PASSWORD=cambiar-por-contraseña-segura

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False  # True para desarrollo, False para producción
```

⚠️ **IMPORTANTE**: 
- **NUNCA** subas el archivo `.env` a Git (usá `.gitignore`)
- Cambia `FLASK_SECRET_KEY` y `SISTEMA_PASSWORD` por valores únicos y seguros
- Las credenciales de Firebase en el servidor se cargan automáticamente desde las variables del servidor

## ▶️ Ejecutar la Aplicación

### En Desarrollo

```bash
# Asegúrate de que el entorno virtual está activado
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

### En Producción (Servidor)

La aplicación ya está configurada para funcionar en el servidor:

1. **Credenciales Firebase** ✅
   - Ya están configuradas como variables de entorno en el servidor
   - El servidor carga automáticamente `FIREBASE_CREDENTIALS_BASE64`
   - No necesitas hacer nada adicional

2. **Servidor WSGI**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```

3. **Variables de entorno en servidor**:
   - `FLASK_SECRET_KEY`: Ya configurada en el servidor
   - `SISTEMA_PASSWORD`: Ya configurada en el servidor
   - `FIREBASE_CREDENTIALS_BASE64`: Ya configurada en el servidor
   - `FLASK_DEBUG=False`: Desactivado en producción

4. **Seguridad**:
   - ✅ HTTPS habilitado
   - ✅ Credenciales protegidas en variables del servidor
   - ✅ Logs centralizados
   - ✅ Rate limiting implementado

## 📁 Estructura del Proyecto

```
project-root/
├── app.py                          # Aplicación Flask principal
├── requirements.txt                # Dependencias Python
├── README.md                       # Esta documentación
├── .env.example                    # Plantilla de ejemplo (SÍ subir a Git)
├── .gitignore                      # Archivos a ignorar en Git
├── venv/                           # ⚠️ NO SUBIR A GIT (entorno virtual)
├── static/                         # Archivos estáticos (CSS, imágenes)
│   └── *.png                       # Logos e iconos
└── templates/                      # Plantillas HTML
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── form.html

# Archivos generados (⚠️ NO subir a Git):
# ├── .env                           # Variables de entorno locales
# ├── app.log                        # Archivo de logs
# └── firebase-credentials.json      # SOLO para desarrollo local (si aplica)
```

## 🗄️ Estructura de la Base de Datos Firestore

✅ **La base de datos Firestore ya está configurada en el servidor**

La aplicación usa colecciones de Firestore para:

1. **Colección de usuarios** - Datos de registro y autenticación
   - Email (único)
   - Contraseña (hasheada con werkzeug)
   - Fecha de registro

2. **Colecciones privadas por usuario** - Documentos personales
   - Cada usuario tiene acceso solo a sus registros
   - Datos almacenados en colección con ID único del usuario

3. **Colección compartida (Admin)** - Para acceso administrativo
   - Solo accesible con credenciales admin
   - Agregación de datos de todos los usuarios

La aplicación se conecta automáticamente usando las credenciales del servidor.

## 🔐 Sistema de Autenticación

### Tipos de Acceso:

#### 1. **Usuario Regular**
- Crea cuenta en `/register`
- Login en `/login`
- Solo ve sus propias cirugías
- Los datos se almacenan en su colección privada `{user_id}`

#### 2. **Administrador**
- Accede usando la contraseña especial (`SISTEMA_PASSWORD`)
- Email: cualquiera (se ignora)
- Ve todas las cirugías de todos los usuarios
- Los datos se almacenan en `cirugias_cardiovasculares`

### Características de Seguridad:

- ✅ Contraseñas hasheadas con `werkzeug.security`
- ✅ Sesiones seguras con Flask
- ✅ Decorador `@login_required` en rutas protegidas
- ✅ Logging de intentos de acceso (auditoría)
- ✅ Validación de entrada en todos los formularios
- ✅ Logout seguro que limpia la sesión
- ✅ CSRF protection en formularios
- ✅ Variables de entorno para credenciales sensibles

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

## 🎯 Funcionalidades de la Plataforma

### 🔑 Autenticación (Rutas Públicas)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/register` | GET/POST | Crear nueva cuenta de usuario |
| `/login` | GET/POST | Iniciar sesión (usuario o admin) |
| `/logout` | GET | Cerrar sesión y limpiar datos |

### 📊 Dashboard (Rutas Protegidas)

| Funcionalidad | Descripción |
|---|---|
| **Búsqueda en tiempo real** | Filtra por paciente, procedimiento, cirujano |
| **Filtros avanzados** | Por fecha (desde/hasta) y estado postoperatorio |
| **Estadísticas** | Total cirugías, cirugías del mes, pacientes únicos |
| **Tabla interactiva** | Scroll horizontal en móviles, edición directa |
| **Exportación Excel** | Descarga datos en formato `.xlsx` profesional |
| **Edición rápida** | Haz clic en cualquier fila para editar |
| **Eliminación segura** | Confirmación antes de eliminar |
| **Logout** | Botón en el header para cerrar sesión |

### 📋 Formulario de Cirugía

Campos completos organizados en secciones:

**Datos del Paciente**
- Nombre, edad, sexo, cédula, teléfono
- Peso, altura, grupo sanguíneo

**Antecedentes Médicos**
- Diagnóstico principal
- Comorbilidades (checkboxes)
- Medicamentos previos
- Alergias

**Datos de la Cirugía**
- Fecha y hora (inicio/fin)
- Duración automática
- Procedimiento específico
- Descripción quirúrgica

**Equipo Médico**
- Cirujano principal
- Primer y segundo ayudante
- Anestesiólogo
- Perfusionista

**Parámetros Cardiovasculares**
- FEVI preoperatoria
- Clase funcional NYHA
- Euroscore II
- Tiempo CEC y clampeo
- Número de puentes
- Tipo prótesis/injerto

**Postoperatorio**
- Estado postoperatorio
- Días en UCI, hospitalización, ventilación
- Complicaciones
- Tratamiento postoperatorio

**Seguimiento**
- Fecha de alta
- Próxima cita
- Notas adicionales

### 📡 API REST Endpoints (Protegidos)

```
GET    /api/cirugias              → Obtener todas las cirugías
GET    /api/cirugia/<id>          → Obtener cirugía específica
POST   /api/cirugia               → Crear nueva cirugía
PUT    /api/cirugia/<id>          → Actualizar cirugía
DELETE /api/cirugia/<id>          → Eliminar cirugía
GET    /api/export                → Exportar datos a Excel
GET    /api/estadisticas          → Obtener estadísticas
```

## 📊 Datos Capturados

### Paciente
- ✅ Nombre completo, edad, sexo, cédula
- ✅ Datos antropométricos (peso, altura)
- ✅ Grupo sanguíneo, teléfono

### Antecedentes
- ✅ Diagnóstico principal y comorbilidades
- ✅ Medicamentos previos y alergias
- ✅ Parámetros basales cardiovasculares

### Quirúrgico
- ✅ Procedimiento y descripción detallada
- ✅ Equipo completo (cirujano, ayudantes, anestesista, perfusionista)
- ✅ Tiempos (CEC, clampeo, duración total)
- ✅ Injertos/prótesis utilizadas

### Postoperatorio
- ✅ Estado inmediato
- ✅ Duración UCI y hospitalización
- ✅ Ventilación mecánica
- ✅ Complicaciones y tratamientos
- ✅ Seguimiento y próximas citas

## 📝 Logging y Auditoría

La aplicación registra automáticamente:

- **Intentos de acceso** - Resultado (exitoso/fallido), timestamp
- **Cambios de datos** - Cuándo se crean/actualizan registros
- **Errores críticos** - Excepciones y problemas de conexión

⚠️ **Recomendaciones de seguridad**:
- Guarda logs en directorio seguro (NO en repositorio público)
- Implementa rotación de logs
- Usa servicio centralizado de logs en producción (CloudWatch, ELK, etc.)
- NO registres información sensible (contraseñas, credenciales)
- Cumple con GDPR/privacidad de datos del usuario

## � Configuración de .gitignore

Crea un archivo `.gitignore` en la raíz con:

```
# Firebase
firebase-credentials.json
*.base64

# Entorno Virtual
gqg-venv/
env/
venv/
.venv
ENV/

# Variables de entorno
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/

# Logs
*.log
app.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Excel temporal
~$*.xlsx

# Archivos generados
*.xlsx
```

## 🐛 Solución de Problemas

### ❌ Error: "firebase-credentials.json not found"
**Solución:**
- Este error solo ocurriría si intentas usar credenciales locales
- En el servidor, las credenciales se cargan automáticamente desde variables de entorno
- Para desarrollo local, necesitas crear un archivo `firebase-credentials.json` (opcional)

### ❌ Error: "Permission denied" en Firestore
**Solución:**
- Verifica las reglas de seguridad en Firestore Database > Reglas
- Para desarrollo, permite lectura/escritura a todos
- Usa las reglas proporcionadas en la sección de configuración

### ❌ Error: "Email ya está registrado"
**Solución:**
- El email ya existe en la colección `usuarios`
- Usa otro email o reset la base de datos (en Firestore)

### ❌ La aplicación no inicia / "ModuleNotFoundError"
**Solución:**
```bash
# Verifica que el entorno virtual está activado
# Windows
gqg-venv\Scripts\activate

# macOS/Linux
source gqg-venv/bin/activate

# Reinstala las dependencias
pip install -r requirements.txt

# Verifica Python 3.8+
python --version
```

### ❌ Error: "SISTEMA_PASSWORD no configurada"
**Solución:**
- Crea un archivo `.env` con: `SISTEMA_PASSWORD=contraseña-segura`
- O configura la variable de entorno en el servidor/sistema
- ⚠️ NUNCA hardcodes contraseñas en el código

### ❌ Error 500 en login/registro
**Solución:**
- Revisa `app.log` para detalles del error
- Verifica la conexión a Firebase
- Asegúrate de que Firestore está habilitado en Firebase Console

## 📝 Notas de Desarrollo

### Arquitectura

**Framework**: Flask (Python web framework ligero y flexible)

**Base de datos**: Firebase Firestore (NoSQL, escalable)

**Frontend**: HTML5 + CSS3 + Vanilla JavaScript (sin dependencias pesadas)

**Autenticación**: Sistema con sesiones Flask (considera migrar a Firebase Auth para producción)

### Flujo de Datos

```
Usuario registrado → Login → Sesión Flask → 
Dashboard → API REST → Firebase Firestore →
Datos sincronizados en tiempo real
```

### Patrón de Respuesta API

Todas las respuestas JSON siguen el formato:

```json
{
  "success": true/false,
  "data": {...},
  "message": "Texto descriptivo",
  "error": "Descripción del error (si aplica)"
}
```

### Validación de Datos

- **Frontend**: Validación básica en formularios HTML5
- **Backend**: Validación robusta en Python antes de guardar en Firestore
- **Calidad**: Campos numéricos convertidos a tipo correcto, strings limpiados

### Timestamps

- Todos los registros incluyen `fecha_registro` al crearse
- Se actualiza `fecha_actualizacion` cuando se edita
- Formato ISO 8601: `YYYY-MM-DDTHH:MM:SS.mmmmm`

## 🎯 Próximas Mejoras

- [ ] Autenticación Firebase Auth en lugar de manual
- [ ] Roles y permisos granulares (jefe, residente, enfermería)
- [ ] Reportes estadísticos avanzados
- [ ] Gráficos interactivos (Chart.js)
- [ ] Búsqueda fulltext en Firestore
- [ ] Adjuntar archivos (imágenes, PDFs)
- [ ] Historial de cambios (auditoría completa)
- [ ] Notificaciones por email
- [ ] Modo oscuro/claro
- [ ] API documentada con Swagger
- [ ] Testing automático (pytest)
- [ ] CI/CD con GitHub Actions

## 👨‍⚕️ Información del Autor

**G.Q.G - Gestor Quirúrgico García**

Sistema profesional de registro cardiovascular

Versión: **2.0.0**  
Última actualización: **2026-04-01**  
Licencia: **MIT**

### Cambios en la versión 2.0:
- ✅ Sistema de autenticación multi-usuario
- ✅ Acceso administrativo
- ✅ Logging de auditoría
- ✅ Logout desde dashboard
- ✅ Interfaz responsive mejorada
- ✅ Documentación completa
- ✅ Despliegue en producción (Render, Heroku)

---

## 📞 Soporte

Para reportar bugs o sugerencias, asegúrate de incluir:
- Versión de Python instalada
- Logs del error (`app.log`)
- Pasos para reproducir el problema
- Comportamiento esperado vs actual
