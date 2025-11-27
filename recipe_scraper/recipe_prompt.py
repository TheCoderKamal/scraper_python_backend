import logging
from typing import Dict
from core.config import MAX_TRANSCRIPT_LENGTH

logger = logging.getLogger(__name__)

class RecipePromptBuilder:
    @staticmethod
    def build(data: Dict) -> str:
        """Build prompt for recipe extraction"""
        title = data.get('title', 'Untitled')
        publisher = data.get('publisher_name', 'Unknown')
        caption = data.get('caption', '')
        transcript = data.get('transcript', '')
        platform = data.get('platform', 'unknown')
        is_carousel = data.get('is_carousel', False)
        publisher_comment = data.get('publisher_comment', '')
        
        # Truncate transcript if too long
        if len(transcript) > MAX_TRANSCRIPT_LENGTH:
            transcript = transcript[:MAX_TRANSCRIPT_LENGTH] + "\n\n[Truncated]"
            logger.info(f"Transcript truncated to {MAX_TRANSCRIPT_LENGTH} chars")
        
        # Build content sections
        content_parts = []
        if caption:
            content_parts.append(f"Caption/Description:\n{caption}")
        if publisher_comment:
            content_parts.append(f"\nPublisher's Comment:\n{publisher_comment}")
        if transcript:
            content_parts.append(f"\nTranscript:\n{transcript}")
        
        content = "\n\n".join(content_parts) or "No content available"
        post_type = "carousel" if is_carousel else "single post"
        
        return f"""Extract ALL recipes from this cooking content.

POST INFORMATION:
Title: {title}
Publisher: {publisher}
Platform: {platform}
Type: {post_type}

CONTENT:
{content}

INSTRUCTIONS:
1. If NOT cooking-related, return: {{"recipes": [], "total_recipes": 0}}
2. Return ONLY valid JSON (no markdown)
3. Expand all cooking instructions into detailed, step-by-step actions:
break each step into small, clear actions
include heat levels (low / medium / high)
include estimated times (2-3 min, until golden)
add texture / aroma cues (soft, crispy, fragrant)
add all implied steps (cutting, mixing, heating pans, etc.)

4. Ingredient list should be complete:
include all visible/spoken ingredients
make reasonable quantity estimates
keep notes short (max 50 chars)
NEVER leave quantity or notes empty
If notes missing, add short functional note (for flavor, for seasoning, for garnish, adds heat)
5. Translate EVERYTHING to English
6. Use sequential numbering: recipe_number: 1, 2, 3

OUTPUT JSON:
{{
  "name": "",
  "prepTime": "", 
  "cookTime": "",
  "serve": "4",
  "difficulty": "2",
  "suggestTags": "[#fastfood]",
  "ingrediants": {{
    "salt": "1 tea spoon"
  }},
  "description": "This is the Recipe for Homemade Panipuri.",
  "image": "http://google.com",
  "steps": [
    "boil potatos",
    "smash and mix with herbs"
  ],
  "nutritions": {{}},
  "costPerServe": "string"
}}
"""
