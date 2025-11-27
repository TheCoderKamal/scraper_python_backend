# ===== core/config.py =====
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
STATIC_API_TOKEN = os.getenv('STATIC_API_TOKEN', 'your-secret-token')

WHISPER_MODEL = "whisper-large-v3-turbo"
LLAMA_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

MAX_COMMENTS = 50
MAX_TRANSCRIPT_LENGTH = 20000
MAX_OCR_TEXT_LENGTH = 15000

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600