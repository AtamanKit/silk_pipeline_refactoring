from datetime import datetime
from ipaddress import ip_address
from typing import List

from models import NormalizedHost
from .base_normalizer import BaseNormalizer


class QualysNormalizer(BaseNormalizer):
    def normalize(self, raw_host: dict) -> NormalizedHost:
        hostname = (
            raw_host.get("dnsHostName") or
            raw_host.get("fqdn") or
            raw_host.get("name", "unknown")
        )

        # Collect all unique IP addresses
        ip_strs = sorted({
            iface["HostAssetInterface"]["address"]
            for iface in raw_host.get("networkInterface", {}).get("list", [])
            if "HostAssetInterface" in iface and "address" in iface["HostAssetInterface"]
        })

        # Collect all MAC addresses
        macs = sorted({
            iface["HostAssetInterface"]["macAddress"]
            for iface in raw_host.get("networkInterface", {}).get("list", [])
            if "HostAssetInterface" in iface and "macAddress" in iface["HostAssetInterface"]
        })

        os = raw_host.get("os", "unknown")

        last_seen_str = raw_host.get("agentInfo", {}).get(
            "lastCheckedIn", {}).get("$date")
        last_seen = datetime.fromisoformat(last_seen_str.replace(
            "Z", "")) if last_seen_str else datetime.utcnow()

        agent_id = raw_host.get("agentInfo", {}).get("agentId")

        # Parse IPs
        parsed_ips = self._parse_ips(ip_strs)

        # Build unique key
        # ip_str_sorted = [str(ip) for ip in parsed_ips]
        # unique_key = f"{hostname.lower()}|{'|'.join(ip_str_sorted)}|qualys|{'|'.join(macs)}"

        return NormalizedHost(
            hostname=hostname,
            ip_addresses=parsed_ips,
            os=os,
            last_seen=last_seen,
            vendor=["qualys"],
            agent_id=agent_id,
            mac_addresses=macs,
            # unique_key=unique_key
        )

    def _parse_ips(self, ips: List[str]) -> List:
        return [ip_address(ip) for ip in ips if ip]
