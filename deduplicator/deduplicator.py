from typing import List
from models import NormalizedHost


class HostDeduplicator:
    def __init__(self):
        self._seen_hosts: List[NormalizedHost] = []

    def deduplicate(self, hosts: List[NormalizedHost]) -> List[NormalizedHost]:
        deduped: List[NormalizedHost] = []

        for host in hosts:
            match = self._find_duplicate(host)
            if match:
                merged = self._merge_hosts(match, host)
                # Replace existing match with merged version
                self._seen_hosts[self._seen_hosts.index(match)] = merged
            else:
                self._seen_hosts.append(host)

        return self._seen_hosts

    def _find_duplicate(self, new_host: NormalizedHost) -> NormalizedHost | None:
        for existing in self._seen_hosts:
            if self._is_duplicate(existing, new_host):
                return existing
        return None

    def _is_duplicate(self, a: NormalizedHost, b: NormalizedHost) -> bool:
        if a.hostname.lower() == b.hostname.lower():
            return True

        if set(a.ip_addresses) & set(b.ip_addresses):
            return True

        if set(a.mac_addresses or []) & set(b.mac_addresses or []):
            return True

        return False

    def _merge_hosts(self, a: NormalizedHost, b: NormalizedHost) -> NormalizedHost:
        return NormalizedHost(
            hostname=a.hostname or b.hostname,
            ip_addresses=list(set(a.ip_addresses + b.ip_addresses)),
            os=a.os if a.os != "unknown" else b.os,
            last_seen=max(a.last_seen, b.last_seen),
            vendor=f"{a.vendor},{b.vendor}" if b.vendor not in a.vendor else a.vendor,
            agent_id=a.agent_id or b.agent_id,
            mac_addresses=list(set((a.mac_addresses or []) + (b.mac_addresses or [])))
        )
