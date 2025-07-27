import os, sys, itertools, threading, time
import asyncio
from dotenv import load_dotenv

from api_clients import QualysClient, CrowdstrikeClient
from workers.parallel_tasks import vendor_worker
from db import AsyncMongoDBClient
from visualizations.generate_charts import generate_all_charts
from models import NormalizedHost

load_dotenv()

def spinner():
    for char in itertools.cycle('|/-\\'):
        print(f'\r Working... still in progress... {char}', flush=True)
        time.sleep(5)

async def process_vendor(client, vendor: str, db: AsyncMongoDBClient):
    processed = 0
    saved = 0
    async for normalized_host in vendor_worker(client.fetch_hosts(), vendor):
        saved += await db.save_hosts([normalized_host])  # Save each host as it comes
        processed += 1
    print(f"{vendor.capitalize()} processed: {processed}, saved: {saved} (after deduplication)")

async def main():
    # Load API tokens
    token_qualys = os.getenv("API_TOKEN_QUALYS")
    token_crowdstrike = os.getenv("API_TOKEN_CROWDSTRIKE")

    # Initialize clients
    qualys_client = QualysClient(token_qualys)
    crowdstrike_client = CrowdstrikeClient(token_crowdstrike)

    # Initialize MongoDB client and ensure indexes
    db = AsyncMongoDBClient()
    await db._ensure_indexes()

    # Step 1–3: Stream fetch, normalize, and store concurrently
    await asyncio.gather(
        process_vendor(qualys_client, "qualys", db),
        process_vendor(crowdstrike_client, "crowdstrike", db)
    )

    print("All vendors processed and data saved.")

    total = await db.collection.estimated_document_count()
    print(f"Total unique hosts in database: {total}")

    # Step 4: Generate charts from DB data
    all_hosts = await db.fetch_all_hosts()
    generate_all_charts(all_hosts)
    print("Generated charts in visualizations/charts/")

if __name__ == "__main__":
    threading.Thread(target=spinner, daemon=True).start()

    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()

    print(f"Script completed in {end_time - start_time:.2f} seconds")
