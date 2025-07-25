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
        # self.client = MongoClient(MONGO_URI)
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        # self.collection: Collection = self.db[MONGO_COLLECTION]
        # self._ensure_indexes()
        self.collection = self.db[MONGO_COLLECTION]

    async def _ensure_indexes(self):
        await self.collection.create_index([("hostname", ASCENDING)])
        await self.collection.create_index([("ip_addresses", ASCENDING)])
        await self.collection.create_index([("mac_addresses", ASCENDING)])
        await self.collection.create_index([("agent_id", ASCENDING)])
        await self.collection.create_index([("vendor", ASCENDING)])

    async def save_hosts(self, hosts: List[NormalizedHost]):
        for host in hosts:
            # Convert model to dict
            doc = host.dict()

            # Convert IP address objects to strings
            doc["ip_addresses"] = [str(ip) for ip in doc.get("ip_addresses", [])]

            # Convert MAC address objects to strings (if they are not already)
            doc["mac_addresses"] = [str(mac) for mac in doc.get("mac_addresses", [])]
            
            # Perform an upsert (replace if exists, insert otherwise)
            await self.collection.update_one(
                {"hostname": host.hostname, "vendor": host.vendor},
                {"$set": doc},
                upsert=True
            )

    async def fetch_all_hosts(self) -> List[NormalizedHost]:
        cursor = self.collection.find()
        hosts = []
        async for doc in cursor:
            hosts.append(NormalizedHost(**doc))
        return hosts
