import time
import requests
from typing import Optional


class BaseAPIClient:
    BASE_URL: str
    TOKEN: str
    LIMIT: int = 1
    RATE_LIMIT_DELAY: float = 1.0  # 1 request per second
    _last_request_time: float = 0.0

    def __init__(self, token: str):
        self.TOKEN = token

    def _make_request(self, url: str, method: str = 'POST', data: Optional[dict] = None) -> Optional[dict]:
        # Throttle request rate
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            wait_time = self.RATE_LIMIT_DELAY - elapsed
            print(f"Throttling: sleeping for {wait_time:.2f}s")
            time.sleep(wait_time)

        self._last_request_time = time.time()  # Update timestamp

        try:
            response = requests.request(
                method,
                url,
                headers={"accept": "application/json", "token": self.TOKEN},
                json=data or {},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
