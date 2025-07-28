from datetime import datetime
from ipaddress import ip_address
from typing import List

from models import NormalizedHost
from .base_normalizer import BaseNormalizer


class CrowdstrikeNormalizer(BaseNormalizer):
    def normalize(self, raw_host: dict) -> NormalizedHost:
        hostname = raw_host.get("hostname", "unknown")

        # Extract IP addresses – prefer structured ones if available
        ip_strs = []
        if raw_host.get("local_ip"):
            ip_strs.append(raw_host["local_ip"])
        if raw_host.get("external_ip"):
            ip_strs.append(raw_host["external_ip"])
        if raw_host.get("connection_ip") and raw_host["connection_ip"] not in ip_strs:
            ip_strs.append(raw_host["connection_ip"])

        # Extract MACs – CrowdStrike usually has one, but sometimes more
        macs = []
        if raw_host.get("mac_address"):
            macs.append(raw_host["mac_address"].replace("-", ":"))
        if raw_host.get("connection_mac_address") and raw_host["connection_mac_address"] not in macs:
            macs.append(raw_host["connection_mac_address"].replace("-", ":"))

        # Parse the last seen time
        last_seen_str = raw_host.get("last_seen")
        last_seen = datetime.fromisoformat(last_seen_str.replace(
            "Z", "")) if last_seen_str else datetime.utcnow()

        # Normalize IPs and MACs
        # parsed_ips = self._parse_ips(ip_strs)
        # normalized_macs = sorted(macs) if macs else []

        # Construct unique key
        # ip_str_sorted = [str(ip) for ip in sorted(parsed_ips)]
        # unique_key = f"{hostname.lower()}|{'|'.join(ip_str_sorted)}|crowdstrike|{'|'.join(normalized_macs)}"

        return NormalizedHost(
            hostname=hostname,
            ip_addresses=self._parse_ips(ip_strs),
            os=raw_host.get("os_version", "unknown"),
            last_seen=last_seen,
            vendor=["crowdstrike"],
            agent_id=raw_host.get("device_id"),
            mac_addresses=macs or None,
            # unique_key=unique_key
        )

    def _parse_ips(self, ips: List[str]) -> List:
        return [ip_address(ip) for ip in ips if ip]
