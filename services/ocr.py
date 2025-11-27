import logging
import base64
from typing import Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from core.config import GROQ_API_KEY, VISION_MODEL

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service using Groq Vision API"""
    
    def __init__(self):
        self.client = self._init_client()
        if self.client:
            logger.info("OCR Service initialized successfully")
    
    def _init_client(self) -> Optional[Groq]:
        """Initialize Groq client"""
        if not GROQ_AVAILABLE:
            logger.error("Groq library not available. Install with: pip install groq")
            return None
        
        if not GROQ_API_KEY:
            logger.error("GROQ_API_KEY not found in environment variables")
            return None
        
        try:
            client = Groq(api_key=GROQ_API_KEY)
            logger.info("Groq client initialized for OCR")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            return None
    
    def extract_text(self, image_bytes: bytes) -> Optional[str]:
        """
        Extract text from image using Groq Vision API
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Extracted text or None if OCR fails
        """
        if not self.client:
            logger.error("Groq client not available for OCR")
            return None
        
        try:
            logger.info(f"Starting OCR extraction for image ({len(image_bytes)} bytes)")
            
            # Convert image bytes to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Detect image format
            image_format = self._detect_image_format(image_bytes)
            logger.info(f"Detected image format: {image_format}")
            
            data_url = f"data:image/{image_format};base64,{base64_image}"
            
            logger.info(f"Calling Groq Vision API with model: {VISION_MODEL}")
            
            # Call Groq Vision API
            completion = self.client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url
                                }
                            },
                            {
                                "type": "text",
                                "text": """Extract ALL text visible in this image. 

Instructions:
1. Transcribe every word, number, and text element exactly as shown
2. Maintain the original structure and formatting where possible
3. Include ingredient lists, measurements, instructions, titles, and any other text
4. If the image contains a recipe, extract all components (ingredients, steps, notes)
5. Return only the extracted text, no additional commentary
6. Preserve line breaks and section separations

Format the output clearly with proper line breaks between sections."""
                            }
                        ]
                    }
                ],
                temperature=1,
                max_completion_tokens=2000,
                top_p=1,
                stream=False
            )
            
            extracted_text = completion.choices[0].message.content.strip()
            
            logger.info(f"OCR extraction successful. Extracted {len(extracted_text)} characters")
            logger.debug(f"Extracted text preview: {extracted_text[:200]}...")
            
            return extracted_text
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {type(e).__name__} - {str(e)}")
            return None
    
    @staticmethod
    def _detect_image_format(image_bytes: bytes) -> str:
        """
        Detect image format from bytes header
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Image format (jpeg, png, webp, etc.)
        """
        if image_bytes[:2] == b'\xff\xd8':
            return 'jpeg'
        elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return 'png'
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return 'webp'
        elif image_bytes[:2] == b'BM':
            return 'bmp'
        elif image_bytes[:4] == b'GIF8':
            return 'gif'
        else:
            logger.warning("Unknown image format, defaulting to jpeg")
            return 'jpeg'