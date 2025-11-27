import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from recipe_scraper.groq_client import GroqClient
from recipe_scraper.audio_handler import AudioHandler
from recipe_scraper.instagram_scraper import InstagramScraper, INSTALOADER_AVAILABLE
from recipe_scraper.video_scraper import VideoScraper
from recipe_scraper.recipe_prompt import RecipePromptBuilder
from recipe_scraper.helpers import URLHelper
from recipe_scraper.models import ScrapedContent
from core.config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

class RecipeScraper:
    def __init__(self, download_dir: Path = DOWNLOAD_DIR):
        self.download_dir = download_dir
        self.download_dir.mkdir(exist_ok=True)
        self.groq = GroqClient()
        self.audio = AudioHandler(self.download_dir)
        self.instagram = InstagramScraper()
        self.video = VideoScraper()
        logger.info("Recipe scraper initialized")
    
    def scrape(self, url: str) -> Optional[Dict]:
        """Main scraping orchestrator"""
        logger.info("="*80)
        logger.info(f"Starting extraction: {url}")
        logger.info("="*80)
        
        base_url = URLHelper.remove_img_index(url)
        
        logger.info("STAGE 1/4: Extracting metadata")
        content = self._extract_metadata(base_url)
        if not content:
            logger.error("Metadata extraction failed")
            return None
        
        logger.info("STAGE 2/4: Checking captions")
        logger.info(f"Captions: {len(content.caption_text) if content.caption_text else 0} chars")
        
        logger.info("STAGE 3/4: Processing media")
        items = (self._process_carousel(base_url, content) if content.is_carousel 
                else self._process_single(base_url, content))
        
        complete_data = self._build_data(base_url, content, items)
        
        logger.info("STAGE 4/4: Extracting recipes")
        recipes = self.groq.extract_recipes(RecipePromptBuilder.build(complete_data))
        
        if not recipes:
            logger.warning("No recipes extracted")
            return {"recipes": [], "total_recipes": 0}
        
        logger.info("Extraction complete")
        logger.info("="*80)
        return recipes
    
    def _extract_metadata(self, url: str) -> Optional[ScrapedContent]:
        """Extract metadata using yt-dlp and fallback to instaloader if needed"""
        logger.info("Using yt-dlp as primary scraper")
        content = self.video.scrape(url, extract_comments=True)
        
        if URLHelper.is_instagram(url) and INSTALOADER_AVAILABLE:
            needs_fallback = (not content or 
                            (not content.description and not content.is_video) or 
                            not content.publisher_comment)
            
            if needs_fallback:
                reason = "yt-dlp failed" if not content else "missing caption/comment"
                logger.info(f"Trying instaloader: {reason}")
                fallback = self.instagram.scrape(url)
                
                if fallback:
                    if content:
                        # Merge data
                        if not content.description and fallback.description:
                            content.description = fallback.description
                        if not content.publisher_comment and fallback.publisher_comment:
                            content.publisher_comment = fallback.publisher_comment
                        if not content.hashtags and fallback.hashtags:
                            content.hashtags = fallback.hashtags
                        return content
                    return fallback
        
        if content:
            logger.info(f"yt-dlp data: {'complete' if content.publisher_comment else 'no publisher comment'}")
            return content
        
        logger.error("All scraping failed")
        return None
    
    def _process_single(self, url: str, content: ScrapedContent) -> List[Dict]:
        """Process single media item"""
        media_type = 'VIDEO' if content.is_video else 'IMAGE'
        logger.info(f"Processing single {media_type}")
        
        transcript = (content.caption_text if content.caption_text 
                     else (self._transcribe(url) if content.is_video else None))
        
        return [{
            'position': 1, 
            'is_video': content.is_video, 
            'transcript': transcript, 
            'url': content.thumbnail
        }]
    
    def _process_carousel(self, base_url: str, content: ScrapedContent) -> List[Dict]:
        """Process carousel items"""
        logger.info(f"Processing carousel: {len(content.carousel_items)} items")
        
        results = []
        for idx, item in enumerate(content.carousel_items, 1):
            logger.info(f"Processing item {idx}/{len(content.carousel_items)}")
            
            transcript = None
            if item.get('is_video'):
                transcript = self._transcribe(
                    URLHelper.add_img_index(base_url, idx), 
                    idx
                )
            
            results.append({
                'position': idx,
                'is_video': item.get('is_video', False),
                'transcript': transcript,
                'url': URLHelper.add_img_index(base_url, idx),
            })
        
        logger.info(f"Carousel complete: {len(results)} items")
        return results
    
    def _transcribe(self, url: str, item_index: int = 0) -> Optional[str]:
        """Download audio and transcribe"""
        audio_path = self.audio.download(url, item_index)
        if not audio_path:
            return None
        
        transcript = self.groq.transcribe_audio(audio_path)
        self.audio.delete(audio_path)
        return transcript
    
    def _build_data(self, url: str, content: ScrapedContent, items: List[Dict]) -> Dict:
        """Build complete data structure for recipe extraction"""
        caption_parts = []
        if content.title:
            caption_parts.append(content.title)
        if content.description and content.description != content.title:
            caption_parts.append(content.description)
        if content.hashtags:
            caption_parts.append(' '.join(f"#{tag}" for tag in content.hashtags))
        
        caption = '\n\n'.join(caption_parts) or "No caption"
        transcript = '\n\n'.join(
            item['transcript'] for item in items if item.get('transcript')
        )
        
        logger.info(f"Data compiled - Caption: {len(caption)} chars, Transcript: {len(transcript)} chars")
        
        return {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'platform': content.platform,
            'is_carousel': content.is_carousel,
            'total_items': len(items),
            'publisher_name': content.uploader,
            'publisher_id': content.uploader_id,
            'title': content.title,
            'caption': caption,
            'publisher_comment': content.publisher_comment,
            'hashtags': content.hashtags,
            'thumbnail': content.thumbnail,
            'items': items,
            'is_video': content.is_video if not content.is_carousel else None,
            'transcript': transcript,
        }