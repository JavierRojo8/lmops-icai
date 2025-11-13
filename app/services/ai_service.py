import base64
import json
import os
import sys
from typing import Any, Dict

from google import genai
from google.genai.types import Part, GenerateContentConfig

from app.constants import Constants

class GeminiService:
    """Service for processing images with Gemini Vision API"""
    
    def __init__(self, logger):
        self.logger = logger
        self.name = "Gemini_Service"
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initialize Gemini client with API key and model"""
        try:
            self.gemini_client = genai.Client(
                api_key=Constants.GEMINI_API_KEY
            )
            self.model_name = Constants.GEMINI_MODEL
            self.logger.info(
                "Gemini client initialized successfully",
                logger_name=self.name
            )
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Gemini client: {e}",
                logger_name=self.name
            )
            raise

    async def process_image(
        self,
        image_base64: str,
        prompt: str,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Process an image or PDF with Gemini and extract information based on prompt
        
        Args:
            image_base64: Base64 encoded file string (image or PDF)
            prompt: Instructions for what information to extract from the file
            mime_type: MIME type of the file (e.g., 'image/jpeg', 'image/png', 'application/pdf')
            
        Returns:
            Dict with extracted information as JSON
        """
        try:
            file_type = "PDF" if mime_type == "application/pdf" else "imagen"
            self.logger.info(
                f"Starting {file_type} processing with Gemini",
                logger_name=self.name
            )
            
            # Decode base64 file
            try:
                # Remove data URL prefix if present (e.g., "data:image/png;base64,")
                if ',' in image_base64:
                    image_base64 = image_base64.split(',')[1]
                
                file_bytes = base64.b64decode(image_base64)
                self.logger.info(
                    f"Decoded {file_type}: {len(file_bytes)} bytes",
                    logger_name=self.name
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to decode base64 {file_type}: {e}",
                    logger_name=self.name
                )
                raise ValueError(f"Invalid base64 {file_type} data")
            
            # Create the prompt with JSON output requirement
            full_prompt = f"""{prompt}
                IMPORTANTE: Devuelve ÚNICAMENTE un objeto JSON válido con los campos solicitados. 
                No incluyas explicaciones adicionales, solo el JSON.
                """
            # Prepare the content parts for Gemini
            contents = [
                Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type
                ),
                Part.from_text(text=full_prompt)
            ]
            
            # Configure generation
            config = GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
            
            # Generate content
            self.logger.info(
                f"Calling Gemini API for {file_type} analysis",
                logger_name=self.name
            )
            
            response = self.gemini_client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # Extract and parse the response
            if response and response.text:
                result_text = response.text.strip()
                self.logger.info(
                    f"Gemini response received: {result_text[:200]}...",
                    logger_name=self.name
                )
                
                try:
                    # Parse JSON response
                    result = json.loads(result_text)
                    return result
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Failed to parse Gemini response as JSON: {e}",
                        logger_name=self.name
                    )
                    # Return raw text if JSON parsing fails
                    return {"raw_response": result_text}
            else:
                self.logger.warning(
                    "Empty response from Gemini",
                    logger_name=self.name
                )
                return {"error": "No response from Gemini"}
                
        except Exception as e:
            self.logger.error(
                f"Error processing image with Gemini: {e}",
                logger_name=self.name
            )
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.error(
                f"{exc_type} en {fname} línea {exc_tb.tb_lineno}",
                logger_name=self.name
            )
            raise
