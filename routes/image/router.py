# /image/router.py

import logging
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from typing import Dict

from core.security import verify_api_key
from core.rate_limit import rate_limiter
from routes.image.controller import ImageController

router = APIRouter(prefix="/scrape/image", tags=["image"])
logger = logging.getLogger(__name__)

@router.post("")
async def scrape_image(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Extract recipe from image using OCR + LLM
    
    Flow:
    1. Validate image file
    2. Extract text using Groq Vision (OCR)
    3. Parse recipe using Groq Llama
    4. Return structured JSON
    """
    logger.info(f"Image scraping request received: {file.filename} ({file.content_type})")
    
    # Rate limiting
    try:
        rate_limiter.check_rate_limit(api_key)
        logger.debug("Rate limit check passed")
    except HTTPException as e:
        logger.warning(f"Rate limit exceeded for API key")
        raise e
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if not file.content_type or file.content_type not in allowed_types:
        logger.error(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"File must be an image. Allowed: {', '.join(allowed_types)}"
        )
    
    logger.info(f"File type validated: {file.content_type}")
    
    controller = ImageController()
    
    try:
        # Read image bytes
        logger.debug("Reading image bytes from upload")
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            logger.error("Empty image file received")
            raise HTTPException(
                status_code=400,
                detail="Empty image file received"
            )
        
        logger.info(f"Image loaded: {len(image_bytes)} bytes")
        
        # Process image
        logger.info("Starting image processing pipeline")
        result = controller.process(image_bytes)
        
        if not result:
            logger.error("Recipe extraction returned no result")
            raise HTTPException(
                status_code=400,
                detail="Failed to extract recipe from image"
            )
        
        recipe_count = result.get('total_recipes', 0)
        logger.info(f"Request complete: {recipe_count} recipe(s) extracted")
        
        return {
            "success": True,
            "data": result,
            "message": f"Successfully extracted {recipe_count} recipe(s)" if recipe_count > 0 else "No recipes found in image"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Internal server error: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )