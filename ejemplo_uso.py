"""
Ejemplo de uso de la API de procesamiento de imágenes

Este script demuestra cómo usar la API para extraer información de una imagen.
"""

import base64
import requests
import json


def encode_image_to_base64(image_path: str) -> str:
    """
    Codifica una imagen a base64
    
    Args:
        image_path: Ruta al archivo de imagen
        
    Returns:
        String con la imagen codificada en base64
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def process_image(api_url: str, image_base64: str, prompt: str) -> dict:
    """
    Procesa una imagen usando la API
    
    Args:
        api_url: URL del endpoint de la API
        image_base64: Imagen codificada en base64
        prompt: Instrucciones sobre qué extraer de la imagen
        
    Returns:
        Respuesta de la API con los datos extraídos
    """
    response = requests.post(
        api_url,
        json={
            "file_base64": image_base64,
            "prompt": prompt
        },
        headers={"Content-Type": "application/json"}
    )
    
    response.raise_for_status()
    return response.json()


def main():
    # Configuración
    API_URL = "http://localhost:8000/v1/image/process-image"
    
    # Ejemplo 1: Procesar volante MAPFRE Salud con prompt por defecto
    print("=" * 80)
    print("EJEMPLO 1: Procesamiento de Volante MAPFRE Salud (prompt por defecto)")
    print("=" * 80)
    
    # Reemplaza con la ruta a tu volante
    volante_path = r"C:\Users\javir\Downloads\Volante.png"

    try:
        # Codificar imagen
        print(f"Codificando volante: {volante_path}")
        image_base64 = encode_image_to_base64(volante_path)
        
        # NO necesitas proporcionar prompt, usa el por defecto
        print(f"Procesando volante con Gemini (usando prompt por defecto)...")
        
        # Request sin prompt - usa el prompt por defecto optimizado para volante MAPFRE
        response = requests.post(
            API_URL,
            json={
                "file_base64": image_base64
                # Sin prompt - se usa el por defecto
            },
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        print("\n✅ Campos extraídos del volante MAPFRE Salud:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Mostrar campos específicos
        if "extracted_data" in result:
            data = result["extracted_data"]
            print("\n📋 Resumen de campos principales:")
            print(f"  - Número documento: {data.get('numero_documento', 'N/A')}")
            print(f"  - Filiación asegurado: {data.get('filiacion_asegurado', 'N/A')}")
            print(f"  - Prescripción: {data.get('prescripcion', 'N/A')}")
            print(f"  - Fecha primeros síntomas: {data.get('fecha_primeros_sintomas', 'N/A')}")
            print(f"  - Origen patología: {data.get('origen_patologia', 'N/A')}")
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el volante en {volante_path}")
        print("Por favor, actualiza la variable 'volante_path' con la ruta correcta")
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar con la API")
        print("Asegúrate de que el servidor está ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 2: Procesar con prompt personalizado
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Procesamiento con prompt personalizado")
    print("=" * 80)
    
    prompt_personalizado = """
    Extrae SOLO estos campos del volante:
    - numero_documento: número del volante
    - filiacion_asegurado: nombre del paciente
    - prescripcion: qué tratamiento se prescribe
    - fecha_primeros_sintomas: cuándo comenzaron los síntomas
    """
    
    print("Este ejemplo muestra cómo usar un prompt personalizado")
    print("Descomenta el código para probar:")
    
    # try:
    #     image_base64 = encode_image_to_base64("ruta/a/volante.jpg")
    #     response = requests.post(
    #         API_URL,
    #         json={
    #             "image_base64": image_base64,
    #             "prompt": prompt_personalizado  # Prompt personalizado
    #         },
    #         headers={"Content-Type": "application/json"}
    #     )
    #     response.raise_for_status()
    #     result = response.json()
    #     print(json.dumps(result, indent=2, ensure_ascii=False))
    # except Exception as e:
    #     print(f"Error: {e}")


if __name__ == "__main__":
    main()
