import logging
from typing import Optional, List
import yt_dlp

from recipe_scraper.models import ScrapedContent
from recipe_scraper.caption_extractor import YouTubeCaptionExtractor
from core.config import MAX_COMMENTS

logger = logging.getLogger(__name__)

class VideoScraper:
    @staticmethod
    def scrape(url: str, extract_comments: bool = True) -> Optional[ScrapedContent]:
        """Scrape video metadata using yt-dlp"""
        try:
            options = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'ignoreerrors': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'allsubtitles': True,
                'getcomments': extract_comments,
            }
            
            logger.info("Extracting metadata with yt-dlp")
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logger.error("No metadata extracted")
                    return None
                
                platform = info.get('extractor', '').lower()
                
                # Extract captions for YouTube videos
                caption_text = None
                if 'youtube' in platform or 'youtu.be' in url.lower():
                    caption_text = YouTubeCaptionExtractor.extract(info)
                
                comments = info.get('comments', [])
                publisher_comment = VideoScraper._find_publisher_comment(
                    comments, 
                    info.get('uploader_id', ''), 
                    info.get('channel_id', '')
                )
                
                logger.info(f"Platform: {platform}, Comments: {len(comments)}, Publisher: {'FOUND' if publisher_comment else 'NOT FOUND'}")
                
                return ScrapedContent(
                    title=info.get('title', ''),
                    description=info.get('description', ''),
                    platform=platform,
                    uploader=info.get('uploader', info.get('channel', '')),
                    uploader_id=info.get('uploader_id', info.get('channel_id', '')),
                    thumbnail=info.get('thumbnail', ''),
                    hashtags=info.get('hashtags', []),
                    comments=comments[:MAX_COMMENTS],
                    publisher_comment=publisher_comment,
                    is_video=True,
                    caption_text=caption_text
                )
        except Exception as e:
            logger.error(f"Video scraping failed: {e}")
            return None
    
    @staticmethod
    def _find_publisher_comment(comments: List, uploader_id: str, channel_id: str) -> str:
        """Find comment from publisher/channel owner"""
        publisher_ids = {uploader_id, channel_id}
        logger.info(f"Searching for publisher comment in {len(comments)} comments")
        
        for idx, comment in enumerate(comments):
            if idx < 3:
                logger.info(f"Comment {idx}: author={comment.get('author', '')}, id={comment.get('author_id', '')}")
            
            if comment.get('author_id', '') in publisher_ids:
                text = comment.get('text', '')
                if text:
                    logger.info(f"Publisher comment found at position {idx}")
                    return text
        
        logger.warning("Publisher comment not found")
        return ""