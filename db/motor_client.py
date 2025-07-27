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
        # Unique index for deduplication
        await self.collection.create_index(
            [("unique_key", ASCENDING)],
            unique=True
        )
        # Optional secondary indexes
        await self.collection.create_index([("hostname", ASCENDING)])
        await self.collection.create_index([("ip_addresses", ASCENDING)])
        await self.collection.create_index([("mac_addresses", ASCENDING)])
        await self.collection.create_index([("agent_id", ASCENDING)])
        await self.collection.create_index([("vendor", ASCENDING)])

    async def save_hosts(self, hosts: List[NormalizedHost]) -> int:
        upserted_count = 0
        
        for host in hosts:
            # Convert model to dict
            doc = host.dict()

            # Convert IP address objects to strings
            doc["ip_addresses"] = [str(ip) for ip in doc.get("ip_addresses", [])]

            # Convert MAC address objects to strings
            doc["mac_addresses"] = [str(mac) for mac in doc.get("mac_addresses", [])]

            # Perform an upsert based on unique_key
            result =await self.collection.update_one(
                {"unique_key": host.unique_key},
                {"$set": doc},
                upsert=True
            )

            # If the document was inserted (not just updated))
            if result.upserted_id or result.modified_count > 0:
                upserted_count += 1

        return upserted_count

    async def fetch_all_hosts(self) -> List[NormalizedHost]:
        cursor = self.collection.find()
        hosts = []
        async for doc in cursor:
            hosts.append(NormalizedHost(**doc))
        return hosts
