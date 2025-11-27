import os
import re
import json
import logging
from typing import Optional, Dict

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from core.config import GROQ_API_KEY, WHISPER_MODEL, LLAMA_MODEL

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.client = self._init_client()
    
    def _init_client(self) -> Optional[Groq]:
        """Initialize Groq client"""
        if not GROQ_AVAILABLE:
            logger.warning("Groq library not available")
            return None
        
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not found")
            return None
        
        try:
            return Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            logger.error(f"Groq init failed: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file using Whisper"""
        if not self.client:
            return None
        
        try:
            logger.info(f"Transcribing: {os.path.basename(audio_path)}")
            with open(audio_path, "rb") as f:
                result = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), f.read()),
                    model=WHISPER_MODEL,
                    response_format="verbose_json",
                    temperature=0.0
                )
            logger.info(f"Transcription complete: {len(result.text)} chars")
            return result.text.strip()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def extract_recipes(self, prompt: str) -> Optional[Dict]:
        """Extract recipes using Llama"""
        if not self.client:
            return None
        
        try:
            logger.info("Extracting recipes with Llama")
            response = self.client.chat.completions.create(
                model=LLAMA_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional recipe extraction AI. Extract recipes and return ONLY valid JSON. No markdown, no explanations."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=8000,
                top_p=0.95
            )
            
            result = self._parse_json(response.choices[0].message.content.strip())
            logger.info("Recipe extraction " + ("successful" if result else "failed"))
            return result
        except Exception as e:
            logger.error(f"Recipe extraction failed: {e}")
            return None
    
    @staticmethod
    def _parse_json(content: str) -> Optional[Dict]:
        """Parse JSON from LLM response, handling markdown code blocks"""
        # Remove markdown code blocks
        content = re.sub(r'^```(?:json)?\n?', '', content)
        content = re.sub(r'\n?```$', '', content).strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON object from text
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return None