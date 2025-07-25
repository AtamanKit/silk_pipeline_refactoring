from typing import AsyncGenerator
from .base_client import AsyncBaseAPIClient


class QualysClient(AsyncBaseAPIClient):
    BASE_URL = "https://api.recruiting.app.silk.security/api/qualys/hosts/get"

    async def fetch_hosts(self) -> AsyncGenerator[dict, None]:
        skip = 0
        while True:
            url = f"{self.BASE_URL}?skip={skip}&limit={self.LIMIT}"
            data = await self._make_request(url)

            if data is None:
                print(
                    f"[{self.__class__.__name__}] No more data or server error at skip={skip}. Stopping.")
                break

            for host in data:
                yield host

            if len(data) < self.LIMIT:
                break
            skip += self.LIMIT
