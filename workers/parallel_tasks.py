# workers/parallel_tasks.py
from typing import AsyncGenerator
from normalizers import QualysNormalizer, CrowdstrikeNormalizer
from models import NormalizedHost

async def vendor_worker(raw_host_gen: AsyncGenerator[dict, None], vendor: str) -> AsyncGenerator[NormalizedHost, None]:
    if vendor == "qualys":
        normalizer = QualysNormalizer()
    elif vendor == "crowdstrike":
        normalizer = CrowdstrikeNormalizer()
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")

    async for raw in raw_host_gen:
        yield normalizer.normalize(raw)
