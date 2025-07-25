import time
import aiohttp
import asyncio
from typing import Optional


class AsyncBaseAPIClient:
    BASE_URL: str
    TOKEN: str
    LIMIT: int = 1
    RATE_LIMIT_DELAY: float = 1.0  # 1 request per second
    _last_request_time: float = 0.0

    def __init__(self, token: str):
        self.TOKEN = token

    async def _make_request(self, url: str, method: str = 'POST', data: Optional[dict] = None) -> Optional[dict]:
        # Rate limiting
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            wait_time = self.RATE_LIMIT_DELAY - elapsed
            print(f"Throttling: sleeping for {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

        self._last_request_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers={"accept": "application/json",
                             "token": self.TOKEN},
                    json=data or {},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"API request failed: {e}")
            return None
