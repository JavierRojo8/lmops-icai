# Tarea 1: Endpoint para Detectar el Nombre del Archivo

## 🎯 Objetivo

Crear tu primer endpoint REST que reciba una imagen en Base64 y devuelva información básica sobre ella, incluyendo el tipo de archivo detectado. Esta es una tarea introductoria para familiarizarte con FastAPI y la estructura del proyecto.

---

## 📋 Especificación del Endpoint

### Endpoint
- **Método**: `POST`
- **Ruta**: `/v1/files/get-info`
- **Descripción**: Recibe un archivo en Base64 y devuelve información básica

### Request Body

```json
{
  "file_base64": "string (requerido)",
  "filename": "string (opcional)"
}
```

**Parámetros:**
- `file_base64`: Archivo codificado en Base64
- `filename`: Nombre del archivo (opcional, ej: "volante.pdf")

### Response (200 OK)

```json
{
  "message": "Archivo recibido correctamente",
  "filename": "volante.pdf",
  "file_type": "PDF",
  "file_size_kb": 245.8
}
```

### Response (400 Bad Request)

```json
{
  "detail": "Error al procesar el archivo"
}
```

---

## 🛠️ Pasos a Seguir

### Paso 1: Crear los Modelos Pydantic

Crea un archivo nuevo: `app/models/file_info.py`

```python
# Tarea 1: Crear un Endpoint REST con FastAPI

## 🎯 Objetivo

Aprender a crear un endpoint REST en FastAPI utilizando funciones ya implementadas. En esta tarea **ya tienes las funciones** que hacen el trabajo, tu tarea es **crear el router** e **integrar esas funciones** correctamente en un endpoint REST.

---

## 📋 Especificación del Endpoint

### Endpoint
- **Método**: `POST`
- **Ruta**: `/v1/files/get-info`
- **Descripción**: Recibe un archivo en Base64 y devuelve información básica

### Request Body

```json
{
  "file_base64": "string (requerido)",
  "filename": "string (opcional)"
}
```

**Parámetros:**
- `file_base64`: Archivo codificado en Base64
- `filename`: Nombre del archivo (opcional, ej: "volante.pdf")

### Response (200 OK)

```json
{
  "message": "Archivo recibido correctamente",
  "filename": "volante.pdf",
  "file_type": "PDF",
  "file_size_kb": 245.8
}
```

### Response (400 Bad Request)

```json
{
  "detail": "Error al procesar el archivo"
}
```

---

## 🛠️ Pasos a Seguir

### Paso 1: Crear los Modelos Pydantic (YA IMPLEMENTADO)

Crea un archivo nuevo: `app/models/file_info.py`

**Copia este código completo (ya está hecho):**

```python
from pydantic import BaseModel, Field
from typing import Optional

class FileInfoRequest(BaseModel):
    """Request para obtener información de archivo"""
    file_base64: str = Field(..., description="Archivo en Base64")
    filename: Optional[str] = Field(None, description="Nombre del archivo (opcional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_base64": "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBl",
                "filename": "documento.pdf"
            }
        }

class FileInfoResponse(BaseModel):
    """Response con información del archivo"""
    message: str
    filename: str
    file_type: str
    file_size_kb: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Archivo recibido correctamente",
                "filename": "documento.pdf",
                "file_type": "PDF",
                "file_size_kb": 245.8
            }
        }
```

### Paso 2: Crear el Servicio con las Funciones (YA IMPLEMENTADO)

Crea un archivo nuevo: `app/services/file_info_service.py`

**Copia este código completo (ya está hecho):**

```python
import base64
from typing import Dict

class FileInfoService:
    """Servicio para obtener información de archivos"""
    
    def __init__(self, logger):
        self.logger = logger
        self.name = "FileInfo_Service"
    
    def get_file_info(self, file_base64: str, filename: str = None) -> Dict[str, any]:
        """
        Obtiene información de un archivo en Base64
        
        Args:
            file_base64: Archivo codificado en Base64
            filename: Nombre del archivo (opcional)
            
        Returns:
            Dict con información del archivo
        """
        try:
            # Detectar tipo de archivo
            file_type = self.detect_file_type(file_base64)
            
            # Calcular tamaño
            file_size_kb = self.calculate_file_size(file_base64)
            
            # Si no hay filename, crear uno basado en el tipo
            if not filename:
                extension = file_type.lower() if file_type != "UNKNOWN" else "bin"
                filename = f"archivo.{extension}"
            
            self.logger.info(
                f"File info: {filename}, Type: {file_type}, Size: {file_size_kb}KB",
                logger_name=self.name
            )
            
            return {
                "message": "Archivo recibido correctamente",
                "filename": filename,
                "file_type": file_type,
                "file_size_kb": file_size_kb
            }
            
        except Exception as e:
            self.logger.error(
                f"Error getting file info: {e}",
                logger_name=self.name
            )
            raise
    
    def detect_file_type(self, file_base64: str) -> str:
        """
        Detecta el tipo de archivo mirando los magic numbers
        
        Args:
            file_base64: Archivo en Base64
            
        Returns:
            Tipo de archivo: "PDF", "JPEG", "PNG", o "UNKNOWN"
        """
        try:
            # Limpiar el Base64 si tiene prefijo "data:..."
            if ',' in file_base64:
                file_base64 = file_base64.split(',')[1]
            
            # Decodificar Base64 a bytes
            file_bytes = base64.b64decode(file_base64)
            
            # Verificar los primeros bytes (magic numbers)
            if file_bytes.startswith(b'%PDF'):
                return "PDF"
            elif file_bytes.startswith(b'\x89PNG'):
                return "PNG"
            elif file_bytes.startswith(b'\xff\xd8\xff'):
                return "JPEG"
            else:
                return "UNKNOWN"
                
        except Exception as e:
            self.logger.warning(f"Error detecting file type: {e}")
            return "UNKNOWN"
    
    def calculate_file_size(self, file_base64: str) -> float:
        """
        Calcula el tamaño del archivo en KB
        
        Args:
            file_base64: Archivo en Base64
            
        Returns:
            Tamaño en kilobytes (redondeado a 2 decimales)
        """
        try:
            # Limpiar el Base64 si tiene prefijo
            if ',' in file_base64:
                file_base64 = file_base64.split(',')[1]
            
            # Decodificar a bytes
            file_bytes = base64.b64decode(file_base64)
            
            # Calcular tamaño en KB
            size_bytes = len(file_bytes)
            size_kb = size_bytes / 1024
            
            # Redondear a 2 decimales
            return round(size_kb, 2)
            
        except Exception as e:
            self.logger.warning(f"Error calculating file size: {e}")
            return 0.0
```

### Paso 3: Crear el Router (⭐ TU TAREA PRINCIPAL ⭐)

Ahora viene tu trabajo. Crea un archivo nuevo: `app/routers/file_info.py`

**Este es el código que DEBES completar:**

```python
from fastapi import APIRouter, HTTPException
from app.models.file_info import FileInfoRequest, FileInfoResponse
from app.services.file_info_service import FileInfoService
from app.services.logging_service import ParrotLogger as LoggingService


# TODO 1: Crear el router 
router = # <-- Completa aquí

# TODO 2: Inicializar el logger
logger = # <-- Completa aquí

# TODO 3: Inicializar el servicio FileInfoService pasándole el logger
file_service = # <-- Completa aquí

# TODO 4: Crear el endpoint POST en la ruta "/get-info"
# Pistas:
# - Usa el decorador @router.post()
# - Define response_model=FileInfoResponse
# - Añade summary y description
@router.# <-- Completa el decorador
async def get_file_info(request: FileInfoRequest):
    """
    Obtiene información básica de un archivo
    
    - **file_base64**: Archivo codificado en Base64
    - **filename**: Nombre del archivo (opcional)
    
    Returns información básica del archivo
    """
    try:
        # TODO 5: Llamar al método get_file_info del servicio
        # Pista: file_service.get_file_info(...)
        result = # <-- Completa aquí
        
        # TODO 6: Retornar FileInfoResponse con los datos del result
        # Pista: return FileInfoResponse(**result)
        return # <-- Completa aquí
        
    except Exception as e:
        # TODO 7: Lanzar HTTPException con status_code 400 y el mensaje de error
        raise # <-- Completa aquí
```

### Paso 4: Registrar el Router en la Aplicación (⭐ TU TAREA ⭐)

Abre el archivo `app/app.py` y añade estas líneas:

```python
# TODO 8: Importar el router file_info
# Pista: from app.routers import file_info

# TODO 9: Registrar el router en la aplicación y añade el  prefix="/v1/files"
# Pista: app.include_router(file_info.router)
```

## ✅ Criterios de Evaluación

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| **Modelos creados** | 10% | Archivos creados correctamente (solo copiar) |
| **Servicio creado** | 10% | Archivo del servicio creado correctamente (solo copiar) |
| **Router - Inicialización** | 20% | TODOs 1-3: Router, logger y servicio inicializados |
| **Router - Decorador** | 20% | TODO 4: Decorador del endpoint configurado correctamente |
| **Router - Lógica** | 20% | TODOs 5-7: Llamada al servicio, respuesta y manejo de errores |
| **Integración en app.py** | 15% | TODOs 8-9: Router importado y registrado |
| **Funciona correctamente** | 5% | El endpoint responde bien en Swagger |

**Total: 100 puntos**

---

## 🧪 Cómo Probar tu Endpoint

### Opción 1: Usando Swagger (⭐ Recomendado ⭐)

1. Ejecuta la aplicación:
   ```bash
   poetry run uvicorn app.app:app --reload
   ```

2. Abre tu navegador en: **http://localhost:8000/docs**

3. Busca el endpoint `/v1/files/get-info` en la sección **Files**

4. Haz clic en **"Try it out"**

5. Pega este ejemplo en el body:
   ```json
   {
     "file_base64": "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBl",
     "filename": "test.pdf"
   }
   ```

6. Haz clic en **"Execute"**

7. **Resultado esperado**:
   ```json
   {
     "message": "Archivo recibido correctamente",
     "filename": "test.pdf",
     "file_type": "PDF",
     "file_size_kb": 23.5
   }
   ```

### Opción 2: Usando PowerShell

```powershell
# Leer una imagen y convertirla a Base64
$imageBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\ruta\a\tu\imagen.jpg"))

# Crear el body
$body = @{
    file_base64 = $imageBase64
    filename = "mi_imagen.jpg"
} | ConvertTo-Json

# Llamar al endpoint
Invoke-RestMethod -Uri "http://localhost:8000/v1/files/get-info" `
    -Method Post -Body $body -ContentType "application/json"
```

### Pruebas Recomendadas

Haz al menos 3 pruebas con diferentes tipos de archivos:

1. **PDF**: Debería devolver `"file_type": "PDF"`
2. **JPEG**: Debería devolver `"file_type": "JPEG"`
3. **PNG**: Debería devolver `"file_type": "PNG"`

---

## 📝 Entregables

1. **Código** (4 archivos):
   - ✅ `app/models/file_info.py` (copiado)
   - ✅ `app/services/file_info_service.py` (copiado)
   - ⭐ `app/routers/file_info.py` (completado por ti)
   - ⭐ `app/app.py` (modificado por ti)

2. **Capturas de pantalla**:
   - Swagger mostrando tu nuevo endpoint en la lista
   - Resultado de al menos 2 pruebas exitosas (diferentes tipos de archivo)
   - Código de tu `file_info.py` router

3. **Documento breve** (`SOLUCION_TAREA_1.md`):
   - ¿Qué hace cada TODO que completaste?
   - ¿Cómo probaste que funciona?
   - ¿Tuviste algún problema? ¿Cómo lo resolviste?
   - **Máximo 1 página**

---

## 🎓 Aprendizajes Clave

Al completar esta tarea habrás aprendido:

- ✅ Estructura de un router en FastAPI
- ✅ Cómo usar decoradores `@router.post()`
- ✅ Cómo conectar un servicio con un endpoint
- ✅ Modelos request/response con Pydantic
- ✅ Manejo de errores con `HTTPException`
- ✅ Cómo registrar routers en FastAPI
- ✅ Cómo probar endpoints con Swagger

---

## 💡 Conceptos Importantes

### ¿Qué es un Router?
Un router es un grupo de endpoints relacionados. En FastAPI usamos `APIRouter` para organizar nuestros endpoints por funcionalidad.

### ¿Qué es un Servicio?
Un servicio contiene la lógica de negocio. El router recibe la petición, llama al servicio, y retorna la respuesta.

### ¿Por qué separar Router y Servicio?
- **Router**: Se encarga de HTTP (recibir requests, enviar responses)
- **Servicio**: Se encarga de la lógica (procesar datos, validar, etc.)

Esta separación hace el código más limpio y fácil de mantener.

### Flujo de una Petición

```
1. Usuario hace POST a /v1/files/get-info
2. FastAPI llama a la función get_file_info() del router
3. El router llama a file_service.get_file_info()
4. El servicio procesa el archivo y retorna un dict
5. El router convierte el dict en FileInfoResponse
6. FastAPI envía la respuesta al usuario
```

---

## 🚀 Extensiones Opcionales (Bonus +10 puntos)

Si terminas rápido y quieres más desafío, implementa **UNO** de estos:

### Opción A: Endpoint GET para formatos soportados
Crea un nuevo endpoint `GET /v1/files/supported-formats` que retorne:
```json
{
  "formats": ["PDF", "JPEG", "PNG"],
  "total": 3
}
```

### Opción B: Validación de tamaño
Modifica el servicio para rechazar archivos mayores a 5MB con un mensaje claro.

### Opción C: Más formatos
Añade detección para GIF (`b'GIF89a'` o `b'GIF87a'`) y BMP (`b'BM'`).

---

## ❓ Preguntas Frecuentes

**P: ¿Tengo que entender todo el código del servicio?**  
R: No es necesario entender cada detalle. Lo importante es que sepas **cómo usar el servicio** desde el router.

**P: ¿Qué hago si me da error al importar?**  
R: Verifica que los archivos estén en las carpetas correctas y que los nombres coincidan exactamente.

**P: ¿Cómo sé si está funcionando?**  
R: Si en Swagger ves tu endpoint y al probarlo te da una respuesta 200, ¡funciona!

**P: ¿Puedo cambiar el código del servicio?**  
R: Para esta tarea NO. El objetivo es aprender a integrar código existente, no a modificarlo.

---

## 💻 Checklist Antes de Entregar

- [ ] He creado `app/models/file_info.py` copiando el código
- [ ] He creado `app/services/file_info_service.py` copiando el código
- [ ] He creado `app/routers/file_info.py` y completado todos los TODOs
- [ ] He modificado `app/app.py` para importar y registrar el router
- [ ] La aplicación arranca sin errores
- [ ] Veo mi endpoint en Swagger (http://localhost:8000/docs)
- [ ] He probado el endpoint con al menos 2 tipos de archivo
- [ ] He tomado capturas de pantalla
- [ ] He escrito el documento de solución

---

**Fecha de entrega**: [A definir por el profesor]  
**Peso en la nota final**: [A definir por el profesor]

¡Buena suerte! 🚀

**Tip**: Si te quedas atascado, revisa cómo están hechos los otros routers en `app/routers/agent.py` como referencia.
````
```

### 2. Crear Servicio de Validación

Crear archivo `app/services/validation_service.py`:

```python
import base64
import io
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import PyPDF2

class ValidationService:
    """Service for validating document formats"""
    
    def __init__(self, logger):
        self.logger = logger
        self.name = "Validation_Service"
    
    def validate_document(
        self,
        file_base64: str,
        declared_mime_type: str
    ) -> Dict[str, Any]:
        """
        Validate a Base64 encoded document
        
        Args:
            file_base64: Base64 encoded file string
            declared_mime_type: The MIME type declared by the user
            
        Returns:
            Dict with validation results
        """
        try:
            # TODO: Implementar decodificación de Base64
            # TODO: Detectar el formato real del archivo
            # TODO: Validar que el formato coincide con el declarado
            # TODO: Obtener dimensiones si es imagen
            # TODO: Calcular tamaño del archivo
            # TODO: Verificar que no esté corrupto
            
            pass
            
        except Exception as e:
            self.logger.error(
                f"Error validating document: {e}",
                logger_name=self.name
            )
            raise
    
    def _decode_base64(self, file_base64: str) -> bytes:
        """Decode base64 string to bytes"""
        # TODO: Implementar decodificación
        # Pista: Manejar el caso donde el base64 tiene prefijo "data:image/...;base64,"
        pass
    
    def _detect_format(self, file_bytes: bytes) -> str:
        """Detect file format from bytes"""
        # TODO: Implementar detección de formato
        # Pista: Usar magic numbers (primeros bytes del archivo)
        # - PDF comienza con: %PDF
        # - PNG comienza con: 89 50 4E 47
        # - JPEG comienza con: FF D8 FF
        pass
```

### 3. Crear Router

Crear archivo `app/routers/validation.py`:

```python
from fastapi import APIRouter, HTTPException
from app.models.validation import (
    DocumentValidationRequest,
    DocumentValidationResponse
)
from app.services.validation_service import ValidationService
from app.services.logging_service import LoggingService

router = APIRouter(prefix="/v1/validate", tags=["Validation"])

# Inicializar servicios
logger = LoggingService()
validation_service = ValidationService(logger)

@router.post(
    "/document-format",
    response_model=DocumentValidationResponse,
    summary="Validate document format",
    description="Validates if a Base64 encoded file is a valid image or PDF"
)
async def validate_document_format(request: DocumentValidationRequest):
    """
    Validate document format and integrity
    
    - **file_base64**: Base64 encoded file
    - **mime_type**: Expected MIME type
    
    Returns validation results including format detection and file information
    """
    try:
        # TODO: Llamar al servicio de validación
        # TODO: Manejar errores y retornar respuesta apropiada
        pass
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail={
            "is_valid": False,
            "error": str(e),
            "declared_mime_type": request.mime_type,
            "suggestion": "Please ensure the file is properly encoded in Base64"
        })
    except Exception as e:
        logger.error(f"Unexpected error in validation endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 4. Registrar Router en la Aplicación

Modificar `app/app.py` para incluir el nuevo router:

```python
from app.routers import validation

# Después de las otras inclusiones de routers
app.include_router(validation.router)
```

---

## 📚 Pistas de Implementación

### Detección de Formato por Magic Numbers

Los archivos tienen "números mágicos" (magic numbers) en sus primeros bytes:

```python
def _detect_format(self, file_bytes: bytes) -> str:
    """Detect format by magic numbers"""
    if file_bytes.startswith(b'%PDF'):
        return 'PDF'
    elif file_bytes.startswith(b'\x89PNG'):
        return 'PNG'
    elif file_bytes.startswith(b'\xff\xd8\xff'):
        return 'JPEG'
    else:
        return 'UNKNOWN'
```

### Calcular Tamaño de Archivo

```python
file_size_bytes = len(file_bytes)
file_size_kb = file_size_bytes / 1024
file_size_mb = file_size_kb / 1024
```

---

## ✅ Criterios de Evaluación

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| **Modelos Pydantic** | 15% | Modelos bien definidos con validaciones apropiadas |
| **Decodificación Base64** | 15% | Manejo correcto de Base64 con y sin prefijo |
| **Detección de Formato** | 20% | Detección correcta usando magic numbers |
| **Validación de Imágenes** | 15% | Validación con PIL y extracción de dimensiones |
| **Validación de PDFs** | 15% | Validación con PyPDF2 |
| **Manejo de Errores** | 10% | Errores informativos y apropiados |
| **Logging** | 5% | Logging de operaciones importantes |
| **Documentación** | 5% | Código comentado y docstrings |

**Total: 100 puntos**

---

## 🧪 Casos de Prueba

### Test 1: Imagen JPEG Válida
```bash
# Deberías poder validar una imagen JPEG correctamente
curl -X POST http://localhost:8000/v1/validate/document-format \
  -H "Content-Type: application/json" \
  -d '{
    "file_base64": "<base64_de_imagen_jpeg>",
    "mime_type": "image/jpeg"
  }'
```

**Resultado esperado**: `is_valid: true`, formato detectado correcto, dimensiones presentes

### Test 2: PDF Válido
```bash
# Deberías poder validar un PDF correctamente
curl -X POST http://localhost:8000/v1/validate/document-format \
  -H "Content-Type: application/json" \
  -d '{
    "file_base64": "<base64_de_pdf>",
    "mime_type": "application/pdf"
  }'
```

**Resultado esperado**: `is_valid: true`, formato PDF detectado

### Test 3: Base64 Inválido
```bash
# Debería rechazar Base64 corrupto
curl -X POST http://localhost:8000/v1/validate/document-format \
  -H "Content-Type: application/json" \
  -d '{
    "file_base64": "esto-no-es-base64-valido!!!",
    "mime_type": "image/jpeg"
  }'
```

**Resultado esperado**: Error 400 con mensaje descriptivo

### Test 4: Formato No Coincide
```bash
# Debería detectar cuando el MIME declarado no coincide con el real
curl -X POST http://localhost:8000/v1/validate/document-format \
  -H "Content-Type: application/json" \
  -d '{
    "file_base64": "<base64_de_pdf>",
    "mime_type": "image/jpeg"
  }'
```

**Resultado esperado**: `mime_type_matches: false`

---


---

## 📝 Entregables

1. **Código**:
   - `app/models/validation.py`
   - `app/services/validation_service.py`
   - `app/routers/validation.py`
   - Modificación en `app/app.py`

2. **Documentación** (archivo `TAREA_1_SOLUCION.md`):
   - Explicación de decisiones técnicas
   - Cómo probaste el endpoint
   - Capturas de pantalla de Swagger/resultados
   - Problemas encontrados y cómo los resolviste

3. **Ejemplos de Uso**:
   - Script PowerShell o Python con ejemplos de llamadas al endpoint
   - Al menos 3 casos de prueba diferentes

---

## 🎓 Aprendizajes Clave

Al completar esta tarea habrás aprendido:

- ✅ Crear endpoints REST con FastAPI
- ✅ Definir modelos de request/response con Pydantic
- ✅ Validar y decodificar Base64
- ✅ Detectar formatos de archivo por magic numbers
- ✅ Manejo de errores y excepciones en APIs
- ✅ Logging de operaciones
- ✅ Documentación automática con FastAPI

---

## 💡 Recursos Útiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [File Signatures (Magic Numbers)](https://en.wikipedia.org/wiki/List_of_file_signatures)

---

¡Buena suerte! 🚀
