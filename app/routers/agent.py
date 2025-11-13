import base64
import os
import sys
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_service import GeminiService
from app.services.logging_service import ParrotLogger as appLogger
from app.constants import Constants, ImagePrompts


class ImageRequest(BaseModel):
    """Request model for image/PDF processing"""
    file_base64: str = Field(
        description="Base64 encoded file (image or PDF)"
    )
    mime_type: str = Field(
        default="image/jpeg",
        description="MIME type of the file (e.g., 'image/jpeg', 'image/png', 'application/pdf')"
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Prompt personalizado. Si no se proporciona, se usa el prompt por defecto para volante MAPFRE Salud"
    )
    
    # Mantener compatibilidad con código anterior
    @property
    def image_base64(self) -> str:
        """Alias para compatibilidad con código anterior"""
        return self.file_base64


class ImageResponse(BaseModel):
    """Response model for image processing"""
    extracted_data: Dict


router = APIRouter()


@router.post("/process-image", response_model=ImageResponse)
async def process_image(request: ImageRequest) -> ImageResponse:
    """
    Process an image or PDF and extract information based on the provided prompt
    
    Args:
        request: ImageRequest with base64 encoded file (image or PDF), mime_type, and optional extraction prompt
        
    Returns:
        ImageResponse with extracted data as JSON
        
    Notes:
        - Soporta imágenes (JPEG, PNG) y archivos PDF
        - Si no se proporciona un prompt, se usa el prompt por defecto para volante MAPFRE Salud
        - El prompt por defecto extrae todos los campos del volante médico
    """
    logger = appLogger(name="image_processor")
    
    try:
        # Initialize Gemini service
        gemini_service = GeminiService(logger)
        
        # Usar prompt por defecto si no se proporciona uno personalizado
        prompt_to_use = request.prompt if request.prompt else ImagePrompts.VOLANTE_MAPFRE_PROMPT
        
        # Process file with Gemini
        file_type = "PDF" if request.mime_type == "application/pdf" else "imagen"
        logger.info(f"Processing {file_type} with Gemini", logger_name="ImageProcessor")
        
        result = await gemini_service.process_image(
            image_base64=request.file_base64,
            prompt=prompt_to_use,
            mime_type=request.mime_type
        )
        
        logger.info(f"{file_type.capitalize()} processed successfully", logger_name="ImageProcessor")
        return ImageResponse(extracted_data=result)
        
    except Exception as e:
        logger.error(
            f"Error processing image: {e}",
            logger_name="ImageProcessor"
        )
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"{exc_type} en {fname} línea {exc_tb.tb_lineno}",
            logger_name="ImageProcessor",
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
