import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import yt_dlp

logger = logging.getLogger(__name__)

class AudioHandler:
    def __init__(self, download_dir: Path):
        self.download_dir = download_dir
        self.download_dir.mkdir(exist_ok=True)
    
    def download(self, url: str, item_index: int = 0) -> Optional[str]:
        """Download audio from video URL"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = str(self.download_dir / f'audio_{timestamp}_item{item_index}.%(ext)s')
            
            # Prioritize m4a (AAC 128k) over webm (Opus) for consistent quality
            # This ensures transcription quality matches FFmpeg-converted audio
            options = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': output,
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [],
            }
            
            logger.info(f"Downloading audio for item {item_index}")
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_path = ydl.prepare_filename(info)
                
                if os.path.exists(audio_path):
                    logger.info(f"Audio downloaded: {os.path.basename(audio_path)}")
                    return audio_path
        except Exception as e:
            logger.error(f"Audio download failed: {e}")
        return None
    
    @staticmethod
    def delete(audio_path: str) -> None:
        """Delete audio file after processing"""
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                logger.info(f"Deleted: {os.path.basename(audio_path)}")
            except Exception as e:
                logger.warning(f"Delete failed: {e}")