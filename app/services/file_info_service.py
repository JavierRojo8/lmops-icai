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