import os
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from models import NormalizedHost
from pymongo import ASCENDING

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "silk_pipeline")
MONGO_COLLECTION = "hosts"


class AsyncMongoDBClient:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]

    async def _ensure_indexes(self):
        # Secondary indexes for query performance
        await self.collection.create_index([("hostname", ASCENDING)])
        await self.collection.create_index([("ip_addresses", ASCENDING)])
        await self.collection.create_index([("mac_addresses", ASCENDING)])
        await self.collection.create_index([("agent_id", ASCENDING)])
        await self.collection.create_index([("vendor", ASCENDING)])

    async def save_hosts(self, hosts: List[NormalizedHost]) -> int:
        upserted_count = 0

        for host in hosts:
            doc = host.dict()

            # Normalize IP/MAC addresses to strings
            doc["ip_addresses"] = [str(ip)
                                   for ip in doc.get("ip_addresses", [])]
            doc["mac_addresses"] = [str(mac)
                                    for mac in doc.get("mac_addresses", [])]

            # Deduplication query
            query = {"$or": []}
            if host.hostname:
                query["$or"].append({"hostname": host.hostname})
            if host.ip_addresses:
                query["$or"].append({
                    "ip_addresses": {"$in": [str(ip) for ip in host.ip_addresses]}
                })
            if host.mac_addresses:
                query["$or"].append({
                    "mac_addresses": {"$in": [str(mac) for mac in host.mac_addresses]}
                })

            if query["$or"]:
                existing = await self.collection.find_one(query)
                if existing:
                    existing_vendors = existing.get("vendor", [])
                    if not isinstance(existing_vendors, list):
                        existing_vendors = [existing_vendors]

                    if set(host.vendor).difference(existing_vendors):
                        updated_vendors = sorted(set(existing_vendors + host.vendor))

                        await self.collection.update_one(
                            {"_id": existing["_id"]},
                            {"$set": {"vendor": updated_vendors}}
                        )

                    continue  # skip insert

            try:
                await self.collection.insert_one(doc)
                upserted_count += 1
            except Exception as e:
                print(f"Insert error: {e}")

        return upserted_count

    async def fetch_all_hosts(self) -> List[NormalizedHost]:
        cursor = self.collection.find()
        hosts = []
        async for doc in cursor:
            hosts.append(NormalizedHost(**doc))
        return hosts
