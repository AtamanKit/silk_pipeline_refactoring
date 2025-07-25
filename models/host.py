from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List, Optional
from datetime import datetime


class NormalizedHost(BaseModel):
    hostname: str = Field(..., description="Primary name of the host")
    ip_addresses: List[IPvAnyAddress] = Field(
        ..., description="List of IPv4/IPv6 addresses")
    os: str = Field(..., description="Operating system reported by the vendor")
    last_seen: datetime = Field(...,
                                description="Datetime the host was last seen")
    vendor: str = Field(...,
                        description="Source of the host data, e.g., 'qualys', 'crowdstrike'")
    agent_id: Optional[str] = Field(
        None, description="Optional vendor-specific agent ID")
    mac_addresses: Optional[List[str]] = Field(
        default_factory=list, description="Optional MAC addresses")
