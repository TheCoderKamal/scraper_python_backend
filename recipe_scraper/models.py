from dataclasses import dataclass, field
from typing import Dict, Optional, List

@dataclass
class ScrapedContent:
    title: str
    description: str
    platform: str
    uploader: str
    uploader_id: str
    thumbnail: str
    hashtags: List[str]
    comments: List[Dict]
    publisher_comment: str
    is_video: bool
    is_carousel: bool = False
    carousel_items: List[Dict] = field(default_factory=list)
    caption_text: Optional[str] = None