import os, sys, itertools, threading, time
import asyncio # added for async MongoDB operations
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor

from api_clients import QualysClient, CrowdstrikeClient
# from normalizers import QualysNormalizer, CrowdstrikeNormalizer
# from deduplicator import HostDeduplicator
# from db import MongoDBClient
from db import AsyncMongoDBClient # Updated to use async MongoDB client  
from visualizations.generate_charts import generate_all_charts
from workers import vendor_worker
# from models import NormalizedHost

load_dotenv()

def spinner():
    for char in itertools.cycle('|/-\\'):
        print(f'\r Working... still in progress... {char}', flush=True)
        time.sleep(5)

async def colect(client):
    return [host async for host in client.fetch_hosts()]

async def main():
    # Load API tokens from environment
    token_qualys = os.getenv("API_TOKEN_QUALYS")
    token_crowdstrike = os.getenv("API_TOKEN_CROWDSTRIKE")

    # Initialize clients
    qualys_client = QualysClient(token_qualys)
    crowdstrike_client = CrowdstrikeClient(token_crowdstrike)

    # Step1: Fetch both APIs concurrently (async parallel)
    qualys_raw_hosts, crowdstrike_raw_hosts = await asyncio.gather(
        colect(qualys_client),
        colect(crowdstrike_client)
    )

    print(f"Fetched {len(qualys_raw_hosts)} Qualys hosts")
    print(f"Fetched {len(crowdstrike_raw_hosts)} Crowdstrike hosts")

    # Step2: Parallel normalize + deduplicate
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as executor:
        future_q = loop.run_in_executor(executor, vendor_worker, qualys_raw_hosts, "qualys")
        future_c = loop.run_in_executor(executor, vendor_worker, crowdstrike_raw_hosts, "crowdstrike")

        qualys_hosts, crowdstrike_hosts = await asyncio.gather(future_q, future_c)

    print(f"After deduplication: {len(qualys_hosts) + len(crowdstrike_hosts)} unique hosts")
    
    # Step3: Combine and save
    all_hosts = qualys_hosts + crowdstrike_hosts
    
    db = AsyncMongoDBClient()  # Use async MongoDB client
    await db.save_hosts(all_hosts)  # Save hosts asynchronously
    print("Saved hosts to MongoDB")

    # Generate visualizations
    generate_all_charts(all_hosts)
    print("Generated charts in visualizations/charts/")

if __name__ == "__main__":
    threading.Thread(target=spinner, daemon=True).start()

    start_time = time.time()
    
    asyncio.run(main())

    end_time = time.time()

    duration = end_time - start_time
    print(f"Script completed in {duration: .2f} seconds")
