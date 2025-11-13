# Frontend - Procesamiento de Volantes Médicos MAPFRE

Frontend sencillo para cargar y procesar volantes médicos usando la API de procesamiento de imágenes con Gemini.

## 🚀 Características

- ✅ **Drag & Drop**: Arrastra y suelta imágenes directamente
- ✅ **Vista Previa**: Visualiza la imagen antes de procesarla
- ✅ **Configuración de API**: URL del endpoint configurable
- ✅ **Resultados Formateados**: Visualización clara de todos los campos extraídos
- ✅ **Descarga JSON**: Exporta los resultados en formato JSON
- ✅ **Responsive**: Funciona en desktop y móvil
- ✅ **Sin Dependencias**: HTML, CSS y JavaScript vanilla

## 📋 Requisitos

- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- API de procesamiento ejecutándose (local o remota)

## 🎯 Uso

### Opción 1: Abrir directamente el archivo HTML

```bash
# Simplemente abre el archivo en tu navegador
start frontend/index.html  # Windows
open frontend/index.html   # macOS
xdg-open frontend/index.html  # Linux
```

### Opción 2: Servidor HTTP local (recomendado)

#### Con Python:
```bash
# Python 3
cd frontend
python -m http.server 8080

# Abrir en el navegador: http://localhost:8080
```

#### Con Node.js (npx):
```bash
cd frontend
npx http-server -p 8080

# Abrir en el navegador: http://localhost:8080
```

#### Con VS Code:
1. Instalar extensión "Live Server"
2. Click derecho en `index.html` → "Open with Live Server"

## 🔧 Configuración

### Configurar URL del API

Por defecto, el frontend apunta a: `http://localhost:8000/v1/image/process-image`

Puedes cambiar la URL directamente en la interfaz o modificar el valor por defecto en el HTML:

```javascript
// Línea 272 en index.html
<input type="text" id="apiUrl" value="http://localhost:8000/v1/image/process-image">
```

### Para usar con API en Docker:
```
http://localhost:8000/v1/image/process-image
```

### Para usar con API en Azure:
```
https://your-api.azurewebsites.net/v1/image/process-image
```

## 📸 Cómo Usar

1. **Cargar Imagen**
   - Arrastra y suelta un volante médico
   - O haz clic en "Seleccionar Imagen"

2. **Revisar Preview**
   - Verifica que la imagen se cargó correctamente

3. **Procesar**
   - Haz clic en "🚀 Procesar Volante"
   - Espera unos segundos mientras Gemini analiza la imagen

4. **Ver Resultados**
   - Revisa los 14 campos extraídos del volante
   - Descarga el JSON si lo necesitas

5. **Procesar Otra**
   - Haz clic en "📄 Procesar Otro Volante"

## 🎨 Campos Extraídos

El frontend muestra los siguientes campos del volante MAPFRE:

1. 👤 Filiación del Asegurado
2. 🏥 Código Servicio Concertado
3. 📄 Número de Documento
4. 💊 Prescripción
5. 📅 Fecha Primeros Síntomas
6. 🩺 Motivos/Síntomas
7. ⚕️ Prestación Sanitaria
8. 🔐 Número de Autorización
9. 🏥 Código Servicio Realizador
10. ✍️ Firma Profesional Realizador
11. ✍️ Firma Asegurado
12. ✍️ Firma y Sello Prescriptor
13. 📅 Fecha de Realización
14. 🔍 Origen Patología

## 🔒 Seguridad y CORS

### Desarrollo Local

Si estás ejecutando el API localmente, asegúrate de que FastAPI tenga CORS configurado:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Producción

Para producción, especifica los orígenes permitidos:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "https://mapfre-frontend.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
```

## 📱 Responsive Design

El frontend se adapta automáticamente a diferentes tamaños de pantalla:

- **Desktop**: Vista completa con todos los detalles
- **Tablet**: Diseño optimizado para pantallas medianas
- **Mobile**: Interfaz adaptada para teléfonos

## 🐛 Solución de Problemas

### Error: "Failed to fetch"
- Verifica que el API esté ejecutándose
- Comprueba la URL del API en la configuración
- Revisa la consola del navegador (F12) para más detalles

### Error: "CORS policy"
- El API necesita configurar CORS (ver sección de Seguridad)
- Asegúrate de que `allow_origins` incluya el origen del frontend

### La imagen no se procesa
- Verifica que el archivo sea una imagen válida (JPG, PNG, etc.)
- Comprueba que la imagen no sea demasiado grande (< 10MB recomendado)
- Revisa los logs del API para ver errores específicos

## 🎨 Personalización

### Cambiar Colores

Modifica las variables CSS en la sección `<style>`:

```css
/* Gradiente principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Colores de botones */
.btn-upload {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Cambiar Textos

Busca y reemplaza los textos en el HTML:

```html
<h1>🏥 MAPFRE Salud</h1>
<p>Procesamiento Automático de Volantes Médicos</p>
```

## 📊 Formato de Respuesta Esperado

El frontend espera una respuesta JSON con esta estructura:

```json
{
  "extracted_data": {
    "filiacion_asegurado": "...",
    "codigo_servicio_concertado": "...",
    "numero_documento": "...",
    "prescripcion": "...",
    "fecha_primeros_sintomas": "DD/MM/YYYY",
    "motivos_sintomas": "...",
    "prestacion_sanitaria": "...",
    "numero_autorizacion": "..." ,
    "codigo_servicio_realizador": "...",
    "firma_profesional_realizador": true,
    "firma_asegurado": false,
    "firma_sello_prescriptor": true,
    "fecha_realizacion": "DD/MM/YYYY",
    "origen_patologia": "Enfermedad"
  }
}
```

## 🚀 Despliegue

### Desplegar en Azure Static Web Apps

1. Sube el contenido de `frontend/` a un repositorio Git
2. Crea un Azure Static Web App
3. Conecta con tu repositorio
4. Configura la URL del API en producción

### Desplegar en GitHub Pages

1. Sube `index.html` a tu repositorio
2. Activa GitHub Pages en la configuración
3. Accede a `https://tu-usuario.github.io/repo-name/`

### Desplegar en Netlify

```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Desplegar
cd frontend
netlify deploy --prod
```

## 📄 Licencia

Este frontend es parte del proyecto de Autorizaciones de Salud MAPFRE.

## 🤝 Soporte

Para problemas o sugerencias, contacta al equipo de desarrollo.
