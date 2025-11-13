"""
Constantes y configuracion para el servicio de procesamiento de imagenes medicas
"""
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class ImagePrompts:
    """Clase con los prompts para el procesamiento de imagenes medicas"""
    
    VOLANTE_MAPFRE_PROMPT: str = """
Analiza esta imagen de un volante de prescripcion medica MAPFRE Salud y extrae TODOS los campos siguientes.

OBJETIVO FUNCIONAL:
El modelo debe identificar cada uno de los campos desde la imagen del volante, reconociendo tanto texto impreso como manuscrito, 
y asociando cada dato a su campo correspondiente. El resultado estructurado permitira alimentar el flujo de autorizaciones medicas 
digitales y el registro automatico del siniestro sanitario, minimizando la intervencion manual.

IMPORTANTE: 
- Reconoce tanto texto impreso como manuscrito
- Si un campo no esta visible o legible, devuelve null
- Manten el formato exacto de fechas como aparecen en el documento
- Preserva codigos numericos tal cual estan escritos
- Se preciso en la lectura de firmas (indica true/false segun su presencia)

CAMPOS A EXTRAER (Volante MAPFRE Salud):

1. filiacion_asegurado: Datos del asegurado (nombre, apellidos, NIF o numero de poliza). 
   Ubicacion: Parte superior izquierda, recuadro "1. Filiacion del asegurado"

2. codigo_servicio_concertado: Codigo numerico del servicio o centro medico concertado (cumplimentado a mano).
   Ubicacion: Parte superior media, recuadro "2. Codigo servicio concertado"

3a. numero_documento: Numero unico de identificacion del volante.
   Ubicacion: Esquina superior derecha, formato numerico

3b. Profesional prescriptor: Nombre del medico que prescribe la prestacion. Normalmente viene con el sello y la firma
    Numero de colegiado: Codigo numerico del medico prescriptor. Normalmente viene con el sello y la firma
    Especialidad: Especialidad medica del profesional prescriptor. Normalmente viene con el sello y la firma
    Ubicacion: Parte superior derecha, debajo del numero de documento, y viene en un sello junto con la firma

4. prescripcion: Texto o codigo del acto medico solicitado (incluye descripcion y codigo si estan presentes).
   Ubicacion: Zona central, recuadro "4. Prescripcion"

4a. fecha_primeros_sintomas: Fecha cuando comenzaron los sintomas (formato: DD/MM/YYYY o como aparezca).
   Ubicacion: Debajo de prescripcion, bloque "4a. Fecha primeros sintomas"

4b. motivos_sintomas: Descripcion breve de motivos o sintomas del paciente.
   Ubicacion: Recuadro "4b. Motivos / Sintomas"

5. prestacion_sanitaria: Codigo de acto, numero de sesiones o dias segun baremo literal.
   Ubicacion: Zona media izquierda, bloque "5. Prestacion sanitaria realizada segun baremo literal"

6. numero_autorizacion: Numero de volante autorizado (si requiere autorizacion).
   Ubicacion: Parte media izquierda, bloque "6. En caso de necesitar autorizacion N de volante"

7. codigo_servicio_realizador: Codigo del centro o profesional que realiza la prestacion.
   Ubicacion: Parte inferior izquierda, junto a datos del acto realizado

8. firma_profesional_realizador: Indica si existe firma manuscrita del profesional realizador (true/false).
   Ubicacion: Parte inferior central, recuadro "8. Firma del profesional realizador"

9. firma_asegurado: Indica si existe firma manuscrita del paciente o titular (true/false).
   Ubicacion: Parte inferior derecha, recuadro "9. Firma del asegurado"

10. firma_sello_prescriptor: Indica si existe firma Y sello del medico prescriptor (true/false).
    Ubicacion: Parte inferior central, junto a firma del profesional realizador

11. fecha_realizacion: Fecha de realizacion de la prestacion medica (formato: DD/MM/YYYY o como aparezca).
    Ubicacion: Parte inferior izquierda, recuadro "10. Fecha realizacion prestacion sanitaria"

12. origen_patologia: Categoria del origen de la atencion: "Enfermedad" o "Accidente".
    Ubicacion: Parte inferior izquierda, recuadro "11. Origen patologia"

FORMATO DE SALIDA:
Devuelve UNICAMENTE un objeto JSON valido con todos estos campos. No incluyas explicaciones adicionales.
Ejemplo de estructura esperada:
{
  "filiacion_asegurado": "...",
  "codigo_servicio_concertado": "...",
  "numero_documento": "...",
  "Profesional_prescriptor": "...",
  "Numero_de_colegiado": "...",
   "Especialidad": "...",
  "prescripcion": "...",
  "fecha_primeros_sintomas": "DD/MM/YYYY",
  "motivos_sintomas": "...",
  "prestacion_sanitaria": "...",
  "numero_autorizacion": "..." o null,
  "codigo_servicio_realizador": "...",
  "firma_profesional_realizador": true/false,
  "firma_asegurado": true/false,
  "firma_sello_prescriptor": true/false,
  "fecha_realizacion": "DD/MM/YYYY",
  "origen_patologia": "Enfermedad" o "Accidente"
}
"""


class Constants:
    """Constantes del servicio obtenidas desde AWS Secrets Manager"""
    
    # Configuracion de entorno
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")
    
    # Configuracion de Google Cloud Platform / Gemini
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # Configuracion de logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
