# /social/router.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict

from core.security import verify_api_key
from core.rate_limit import rate_limiter
from routes.social.controller import SocialController

router = APIRouter(prefix="/scrape/social", tags=["social"])

class SocialScrapeRequest(BaseModel):
    url: HttpUrl

class SocialScrapeResponse(BaseModel):
    success: bool
    data: Dict
    message: str = ""

@router.post("", response_model=SocialScrapeResponse)
async def scrape_social(
    request: SocialScrapeRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Scrape recipe from social media URL
    
    Supports: YouTube, Instagram, TikTok, Facebook
    """
    # Rate limiting
    rate_limiter.check_rate_limit(api_key)
    
    controller = SocialController()
    
    try:
        result = controller.process(str(request.url))
        
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract recipe from social media post"
            )
        
        return SocialScrapeResponse(
            success=True,
            data=result,
            message="Recipe extracted successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )