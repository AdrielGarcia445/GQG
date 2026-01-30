# 🚀 GUÍA RÁPIDA DE INICIO - G.Q.G

## Pasos para ejecutar el sistema por primera vez

### 1️⃣ Instalar Python y dependencias

```bash
# Verificar que Python 3.8+ esté instalado
python --version

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configurar Firebase (IMPORTANTE)

#### A. Crear proyecto en Firebase Console

1. Ve a: https://console.firebase.google.com/
2. Clic en "Agregar proyecto"
3. Nombre: `gqg-garcia` (o el que prefieras)
4. Continúa con la configuración predeterminada

#### B. Crear base de datos Firestore

1. En el menú lateral, selecciona **"Firestore Database"**
2. Clic en **"Crear base de datos"**
3. Modo: **"Iniciar en modo de prueba"** (para desarrollo)
4. Ubicación: Selecciona la más cercana (ej: `us-east1`)
5. Clic en **"Habilitar"**

#### C. Descargar credenciales JSON

1. Clic en el ícono de **engranaje** ⚙️ (Configuración del proyecto)
2. Ve a la pestaña **"Cuentas de servicio"**
3. Clic en **"Generar nueva clave privada"**
4. Se descargará un archivo JSON
5. **RENOMBRA** el archivo a: `firebase-credentials.json`
6. **MUEVE** el archivo a la carpeta del proyecto (mismo nivel que app.py)

```
gqg_project/
├── app.py
├── firebase-credentials.json  ← AQUÍ (NO subir a Git)
├── requirements.txt
└── templates/
```

### 3️⃣ Ejecutar la aplicación

```bash
python app.py
```

### 4️⃣ Abrir en el navegador

```
http://localhost:5000
```

---

## ✅ Checklist de Verificación

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Proyecto creado en Firebase Console
- [ ] Firestore Database habilitado
- [ ] Archivo `firebase-credentials.json` en la raíz del proyecto
- [ ] Aplicación corriendo en `localhost:5000`

---

## 🎯 Uso Básico

1. **Dashboard** (`/`): Ver todas las cirugías, buscar, filtrar
2. **Nueva Cirugía** (`/form`): Registrar nueva operación
3. **Editar**: Clic en "✏️ Editar" en cualquier fila del dashboard
4. **Eliminar**: Clic en "🗑️" (con confirmación)
5. **Exportar**: Clic en "📊 Exportar Excel" para descargar datos

---

## ⚠️ Errores Comunes

### "firebase-credentials.json not found"
**Solución**: Asegúrate de que el archivo esté en la raíz del proyecto con ese nombre exacto.

### "Permission denied" en Firestore
**Solución**: Ve a Firestore > Reglas y asegúrate de tener:
```javascript
allow read, write: if true;
```

### Puerto 5000 en uso
**Solución**: Cambia el puerto en `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambiar a 8080
```

---

## 📞 Soporte

Si tienes problemas:
1. Verifica el checklist anterior
2. Revisa los logs en la terminal
3. Consulta el README.md completo
4. Verifica las reglas de Firestore

---

**¡Listo para registrar cirugías! 🫀**
