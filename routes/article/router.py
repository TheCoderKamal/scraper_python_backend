# /article/router.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict

from core.security import verify_api_key
from core.rate_limit import rate_limiter
from routes.article.controller import ArticleController

router = APIRouter(prefix="/scrape/article", tags=["article"])

class ArticleScrapeRequest(BaseModel):
    url: str  # Can be URL or direct text

class ArticleScrapeResponse(BaseModel):
    success: bool
    data: Dict
    message: str = ""

@router.post("", response_model=ArticleScrapeResponse)
async def scrape_article(
    request: ArticleScrapeRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Extract recipe from article URL or text content
    """
    # Rate limiting
    rate_limiter.check_rate_limit(api_key)
    
    controller = ArticleController()
    
    try:
        # Handle both URL and direct text
        result = controller.process(request.url)
        
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract recipe from article"
            )
        
        return ArticleScrapeResponse(
            success=True,
            data=result,
            message="Recipe extracted successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )