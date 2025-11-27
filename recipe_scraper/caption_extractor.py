import json
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class YouTubeCaptionExtractor:
    PREFERRED_LANGS = ['en', 'hi', 'gu', 'es', 'fr', 'de', 'ja', 'ko', 'zh']
    
    @classmethod
    def extract(cls, info_dict: Dict) -> Optional[str]:
        """Extract captions from YouTube video metadata"""
        try:
            logger.info("Extracting YouTube captions")
            
            # Try manual captions first
            caption = cls._try_extract(info_dict.get('subtitles', {}), 'manual')
            if caption:
                return caption
            
            # Fall back to automatic captions
            caption = cls._try_extract(info_dict.get('automatic_captions', {}), 'auto')
            if caption:
                return caption
            
            logger.info("No captions found")
        except Exception as e:
            logger.error(f"Caption extraction failed: {e}")
        return None
    
    @classmethod
    def _try_extract(cls, source: Dict, source_type: str) -> Optional[str]:
        """Try to extract captions from a source (manual or auto)"""
        if not source:
            return None
        
        # Try preferred languages first
        for lang in cls.PREFERRED_LANGS:
            for available_lang, formats in source.items():
                if available_lang.startswith(lang):
                    caption = cls._download(formats)
                    if caption:
                        logger.info(f"Extracted {source_type} captions: {available_lang}")
                        return caption
        
        # Try any available language
        for lang, formats in source.items():
            caption = cls._download(formats)
            if caption:
                logger.info(f"Extracted {source_type} captions: {lang}")
                return caption
        return None
    
    @staticmethod
    def _download(formats: List[Dict]) -> Optional[str]:
        """Download and parse caption file"""
        import urllib.request
        
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        for fmt in formats:
            if fmt.get('ext') == 'json3':
                try:
                    response = urllib.request.urlopen(fmt['url'], timeout=8)
                    data = json.loads(response.read().decode('utf-8'))
                    
                    segments = []
                    for event in data.get('events', []):
                        if 'segs' in event:
                            text = ''.join(
                                seg.get('utf8', '') for seg in event['segs']
                            ).strip()
                            if text:
                                segments.append(text)
                    
                    return '\n'.join(segments) if segments else None
                except Exception:
                    continue
        return None