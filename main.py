import os, sys, itertools, threading, time
import asyncio # added for async MongoDB operations
from dotenv import load_dotenv

from api_clients import QualysClient, CrowdstrikeClient
from normalizers import QualysNormalizer, CrowdstrikeNormalizer
from deduplicator import HostDeduplicator
# from db import MongoDBClient
from db import AsyncMongoDBClient # Updated to use async MongoDB client  
from visualizations.generate_charts import generate_all_charts
# from models import NormalizedHost

load_dotenv()

def spinner():
    for char in itertools.cycle('|/-\\'):
        print(f'\r Working... still in progress... {char}', flush=True)
        time.sleep(5)

async def main():
    # Load API tokens from environment
    token_qualys = os.getenv("API_TOKEN_QUALYS")
    token_crowdstrike = os.getenv("API_TOKEN_CROWDSTRIKE")

    # Initialize clients
    qualys_client = QualysClient(token_qualys)
    crowdstrike_client = CrowdstrikeClient(token_crowdstrike)

    qualys_normalizer = QualysNormalizer()
    crowdstrike_normalizer = CrowdstrikeNormalizer()

    # Fetch + Normalize
    qualys_hosts = [
        qualys_normalizer.normalize(raw_host)
        for raw_host in qualys_client.fetch_hosts()
    ]

    crowdstrike_hosts = [
        crowdstrike_normalizer.normalize(raw_host)
        for raw_host in crowdstrike_client.fetch_hosts()
    ]

    print(f"Fetched {len(qualys_hosts)} Qualys hosts")
    print(f"Fetched {len(crowdstrike_hosts)} Crowdstrike hosts")

    # Combine and deduplicate
    all_hosts = qualys_hosts + crowdstrike_hosts
    deduplicator = HostDeduplicator()
    unique_hosts = deduplicator.deduplicate(all_hosts)
    print(f"After deduplication: {len(unique_hosts)} unique hosts")

    # Save to MongoDB
    # db = MongoDBClient()
    db = AsyncMongoDBClient()  # Use async MongoDB client
    # db.save_hosts(unique_hosts)
    await db._ensure_indexes()
    await db.save_hosts(unique_hosts)  # Save hosts asynchronously
    print("Saved hosts to MongoDB")

    # Generate visualizations
    generate_all_charts(unique_hosts)
    print("Generated charts in visualizations/charts/")

if __name__ == "__main__":
    threading.Thread(target=spinner, daemon=True).start()

    start_time = time.time()
    
    asyncio.run(main())

    end_time = time.time()
    print(f"Completed in {end_time - start_time:.2f} seconds")
