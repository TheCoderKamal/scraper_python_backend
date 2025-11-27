# image/controller.py

import logging
from typing import Optional, Dict

from services.ocr import OCRService
from recipe_scraper.groq_client import GroqClient
from recipe_scraper.recipe_prompt import RecipePromptBuilder
from core.config import MAX_OCR_TEXT_LENGTH

logger = logging.getLogger(__name__)

class ImageController:
    """Controller for image recipe extraction"""
    
    def __init__(self):
        logger.info("Initializing Image Controller")
        self.ocr = OCRService()
        self.groq = GroqClient()
        logger.info("Image Controller initialized successfully")
    
    def process(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Extract recipes from image
        
        Flow:
        1. OCR to extract text from image (Groq Vision)
        2. Pass extracted text to LLM (Groq Llama)
        3. Parse and return structured recipe JSON
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dict containing recipes and metadata
        """
        logger.info(f"Processing image: {len(image_bytes)} bytes")
        
        # Step 1: OCR Text Extraction
        logger.info("Step 1/3: Starting OCR text extraction")
        
        try:
            extracted_text = self.ocr.extract_text(image_bytes)
            
            if not extracted_text or len(extracted_text.strip()) == 0:
                logger.warning("No text extracted from image")
                return {
                    "recipes": [],
                    "total_recipes": 0,
                    "error": "No text found in image"
                }
            
            logger.info(f"OCR extraction complete: {len(extracted_text)} characters, {len(extracted_text.splitlines())} lines")
            
            # Truncate if too long
            if len(extracted_text) > MAX_OCR_TEXT_LENGTH:
                logger.warning(f"Text truncated from {len(extracted_text)} to {MAX_OCR_TEXT_LENGTH} characters")
                extracted_text = extracted_text[:MAX_OCR_TEXT_LENGTH] + "\n\n[Text truncated]"
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {
                "recipes": [],
                "total_recipes": 0,
                "error": f"OCR failed: {str(e)}"
            }
        
        # Step 2: Build Data Structure
        logger.info("Step 2/3: Building data structure for LLM")
        
        data = {
            'title': 'Image Recipe',
            'publisher_name': 'Unknown',
            'caption': extracted_text,
            'transcript': '',
            'platform': 'image',
            'is_carousel': False,
            'publisher_comment': ''
        }
        
        logger.info(f"Data structure prepared with {len(data['caption'])} characters")
        
        # Step 3: Recipe Extraction
        logger.info("Step 3/3: Extracting recipes with LLM")
        
        try:
            prompt = RecipePromptBuilder.build(data)
            logger.info(f"Recipe extraction prompt built: {len(prompt)} characters")
            
            logger.info("Calling LLM for recipe extraction")
            result = self.groq.extract_recipes(prompt)
            
            if not result:
                logger.warning("No recipes extracted from image")
                return {
                    "recipes": [],
                    "total_recipes": 0,
                    "message": "No recipes found in image"
                }
            
            recipe_count = result.get('total_recipes', len(result.get('recipes', [])))
            logger.info(f"Recipe extraction complete: {recipe_count} recipe(s) found")
            
            if recipe_count > 0:
                for idx, recipe in enumerate(result.get('recipes', []), 1):
                    logger.info(f"Recipe {idx}: {recipe.get('name', 'Unnamed')} - {len(recipe.get('ingrediants', {}))} ingredients, {len(recipe.get('steps', []))} steps")
            
            return result
        
        except Exception as e:
            logger.error(f"Recipe extraction failed: {type(e).__name__} - {str(e)}")
            return {
                "recipes": [],
                "total_recipes": 0,
                "error": str(e)
            }