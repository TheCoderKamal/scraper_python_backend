from urllib.parse import urlparse

class PlatformDetector:
    """Detect social media platform from URL"""
    
    PLATFORMS = {
        'youtube.com': 'youtube',
        'youtu.be': 'youtube',
        'instagram.com': 'instagram',
        'tiktok.com': 'tiktok',
        'facebook.com': 'facebook',
        'pinterest.com': 'pinterest',
        'fb.watch': 'facebook',
        'twitter.com': 'twitter',
        'x.com': 'twitter',
    }
    
    @classmethod
    def detect(cls, url: str) -> str:
        """
        Detect platform from URL
        
        Returns:
            Platform name or 'unknown'
        """
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            
            for platform_domain, platform_name in cls.PLATFORMS.items():
                if platform_domain in domain:
                    return platform_name
            
            return 'unknown'
        except Exception:
            return 'unknown'
    
    @classmethod
    def is_supported(cls, url: str) -> bool:
        """Check if platform is supported"""
        return cls.detect(url) != 'unknown'