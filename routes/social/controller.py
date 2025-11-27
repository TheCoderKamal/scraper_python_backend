# social/controller.py

import logging
from typing import Optional, Dict

from recipe_scraper import RecipeScraper
from services.platform_detection import PlatformDetector

logger = logging.getLogger(__name__)

class SocialController:
    """Controller for social media recipe extraction"""
    
    def __init__(self):
        self.scraper = RecipeScraper()
    
    def process(self, url: str) -> Optional[Dict]:
        """
        Process social media URL and extract recipes
        
        Flow:
        1. Detect platform
        2. Fetch metadata (yt-dlp / instaloader)
        3. Download and transcribe audio (if video)
        4. Extract recipes with LLM
        
        Args:
            url: Social media post URL
            
        Returns:
            Dict containing recipes and metadata
        """
        logger.info(f"Processing social media URL: {url}")
        
        # Detect platform
        platform = PlatformDetector.detect(url)
        logger.info(f"Detected platform: {platform}")
        
        if not PlatformDetector.is_supported(url):
            logger.warning(f"Unsupported platform: {platform}")
            return {
                "recipes": [],
                "total_recipes": 0,
                "error": f"Platform '{platform}' is not supported"
            }
        
        # Scrape and extract recipes
        try:
            result = self.scraper.scrape(url)
            return result
        except Exception as e:
            logger.error(f"Error processing social media URL: {e}")
            return {
                "recipes": [],
                "total_recipes": 0,
                "error": str(e)
            }