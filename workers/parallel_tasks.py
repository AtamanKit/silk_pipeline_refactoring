from normalizers import QualysNormalizer, CrowdstrikeNormalizer
from deduplicator import HostDeduplicator
from typing import List


"""Function to handle parallel tasks for normalizing and deduplicating host data."""


def vendor_worker(raw_hosts: List[dict], vendor: str) -> List:
    if vendor == "qualys":
        normalizer = QualysNormalizer()
    elif vendor == "crowdstrike":
        normalizer = CrowdstrikeNormalizer()
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")
    
    normalized = [normalizer.normalize(host) for host in raw_hosts]
    deduplicator = HostDeduplicator()

    return deduplicator.deduplicate(normalized)
