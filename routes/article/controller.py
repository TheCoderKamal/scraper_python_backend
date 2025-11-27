# article/controller.py

import logging
from typing import Optional, Dict

from recipe_scraper.groq_client import GroqClient
from recipe_scraper.recipe_prompt import RecipePromptBuilder

logger = logging.getLogger(__name__)

class ArticleController:
    """Controller for article/text recipe extraction"""
    
    def __init__(self):
        self.groq = GroqClient()
    
    def process(self, text: str) -> Optional[Dict]:
        """
        Extract recipes from plain text
        
        Flow:
        1. Build prompt with text content
        2. Extract recipes with LLM
        
        Args:
            text: Article or recipe text
            
        Returns:
            Dict containing recipes and metadata
        """
        logger.info(f"Processing article text: {len(text)} characters")
        
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided")
            return {
                "recipes": [],
                "total_recipes": 0,
                "error": "Empty text provided"
            }
        
        # Build data structure similar to social media scraping
        data = {
            'title': 'Article',
            'publisher_name': 'Unknown',
            'caption': text,
            'transcript': '',
            'platform': 'article',
            'is_carousel': False,
            'publisher_comment': ''
        }
        
        # Extract recipes
        try:
            prompt = RecipePromptBuilder.build(data)
            result = self.groq.extract_recipes(prompt)
            
            if not result:
                logger.warning("No recipes extracted from article")
                return {
                    "recipes": [],
                    "total_recipes": 0
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return {
                "recipes": [],
                "total_recipes": 0,
                "error": str(e)
            }