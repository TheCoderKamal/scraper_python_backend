import re
import logging
from typing import Optional, Tuple, List, Dict

try:
    import instaloader
    INSTALOADER_AVAILABLE = True
except ImportError:
    INSTALOADER_AVAILABLE = False

from recipe_scraper.models import ScrapedContent
from core.config import MAX_COMMENTS

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.loader = self._init_loader()
    
    def _init_loader(self) -> Optional['instaloader.Instaloader']:
        """Initialize instaloader client"""
        if not INSTALOADER_AVAILABLE:
            logger.warning("Instaloader not available")
            return None
        
        loader = instaloader.Instaloader()
        loader.context.quiet = True
        return loader
    
    def scrape(self, url: str) -> Optional[ScrapedContent]:
        """Scrape Instagram post metadata"""
        if not self.loader:
            return None
        
        try:
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                logger.error("Failed to extract Instagram shortcode")
                return None
            
            logger.info(f"Fetching Instagram post: {shortcode}")
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            comments, publisher_comment = self._extract_comments(post)
            is_carousel = post.typename == 'GraphSidecar'
            carousel_items = self._extract_carousel(post) if is_carousel else []
            
            logger.info(f"Type: {'CAROUSEL' if is_carousel else 'SINGLE'}, Media: {'VIDEO' if post.is_video else 'IMAGE'}")
            logger.info(f"Publisher comment: {'FOUND' if publisher_comment else 'NOT FOUND'}, Comments: {len(comments)}")
            
            return ScrapedContent(
                title=post.title or '',
                description=post.caption or '',
                platform='instagram',
                uploader=post.owner_username,
                uploader_id=str(post.owner_id),
                thumbnail=post.url,
                hashtags=post.caption_hashtags,
                comments=comments,
                publisher_comment=publisher_comment,
                is_video=post.is_video,
                is_carousel=is_carousel,
                carousel_items=carousel_items
            )
        except Exception as e:
            logger.error(f"Instagram scraping failed: {e}")
            return None
    
    @staticmethod
    def _extract_shortcode(url: str) -> Optional[str]:
        """Extract Instagram shortcode from URL"""
        match = re.search(r'instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None
    
    def _extract_comments(self, post) -> Tuple[List[Dict], str]:
        """Extract comments and find publisher comment"""
        comments = []
        publisher_comment = ""
        
        try:
            publisher_username = post.owner_username
            all_comments = list(post.get_comments())
            
            logger.info(f"Found {len(all_comments)} comments")
            
            # Find publisher comment
            for comment in all_comments:
                if comment.owner.username == publisher_username and not publisher_comment:
                    publisher_comment = comment.text
                    logger.info(f"Publisher comment found: {len(comment.text)} chars")
                    break
            
            # Extract top comments
            for comment in all_comments[:MAX_COMMENTS]:
                comments.append({
                    'author': comment.owner.username,
                    'author_id': str(comment.owner.userid),
                    'text': comment.text,
                })
            
            if not publisher_comment:
                logger.warning("Publisher comment not found")
        except Exception as e:
            logger.warning(f"Comment extraction failed: {e}")
        
        return comments, publisher_comment
    
    @staticmethod
    def _extract_carousel(post) -> List[Dict]:
        """Extract carousel items metadata"""
        items = []
        for node in post.get_sidecar_nodes():
            items.append({
                'is_video': node.is_video,
                'url': node.video_url if node.is_video else node.display_url,
            })
        logger.info(f"Carousel items: {len(items)}")
        return items