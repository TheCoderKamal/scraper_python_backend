from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

class URLHelper:
    @staticmethod
    def add_img_index(url: str, index: int) -> str:
        """Add img_index parameter to URL for carousel items"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params['img_index'] = [str(index)]
        return urlunparse((
            parsed.scheme, 
            parsed.netloc, 
            parsed.path, 
            parsed.params, 
            urlencode(params, doseq=True), 
            parsed.fragment
        ))
    
    @staticmethod
    def remove_img_index(url: str) -> str:
        """Remove img_index parameter from URL"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params.pop('img_index', None)
        return urlunparse((
            parsed.scheme, 
            parsed.netloc, 
            parsed.path, 
            parsed.params, 
            urlencode(params, doseq=True), 
            parsed.fragment
        ))
    
    @staticmethod
    def is_instagram(url: str) -> bool:
        """Check if URL is Instagram"""
        return 'instagram.com' in url.lower()