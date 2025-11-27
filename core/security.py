# ===== core/security.py =====
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from core.config import STATIC_API_TOKEN

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != STATIC_API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return api_key


