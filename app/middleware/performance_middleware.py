import asyncio
from fastapi import Request, HTTPException
from app.core.performance_config import performance_settings

# Simple semaphore for concurrent request limiting
request_semaphore = asyncio.Semaphore(performance_settings.MAX_CONCURRENT_REQUESTS)

async def performance_middleware(request: Request, call_next):
    async with request_semaphore:
        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=performance_settings.REQUEST_TIMEOUT
            )
            return response
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Request timeout")
        except Exception as e:
            # Log error for monitoring
            raise