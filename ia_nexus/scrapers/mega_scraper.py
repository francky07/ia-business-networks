#!/usr/bin/env python3
import asyncio, aiohttp, re, random, time, sys, os
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB

SOURCES = ["https://www.leboncoin.fr/offres/", "https://www.freelance-info.fr/annonces"]  # À remplacer
NB_AGENTS, NB_BOOSTERS = 500, 300
RPS = 50
sem = asyncio.Semaphore(RPS)
lead_queue = asyncio.Queue(maxsize=2000)
stats = {"pages":0, "leads":0}

async def fetch(session, url):
    async with sem:
        try:
            async with session.get(url, timeout=10) as resp:
                return await resp.text() if resp.status==200 else None
        except: return None

async def scraper(agent_id, booster=False):
    async with aiohttp.ClientSession() as session:
        while True:
            for src in SOURCES:
                html = await fetch(session, src)
                if html:
                    emails = set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html))
                    for e in emails:
                        await lead_queue.put(e)
                    stats["pages"] += 1
                    if booster: stats.setdefault("boost",0)
            await asyncio.sleep(random.uniform(0.5,2) if booster else random.uniform(2,5))

async def storer():
    while True:
        batch = []
        for _ in range(50):
            try:
                email = await asyncio.wait_for(lead_queue.get(), timeout=1)
                batch.append(email)
            except: break
        if batch:
            for e in batch:
                NexusDB.execute("INSERT OR IGNORE INTO leads (email, source, date_ajout) VALUES (?,?,?)",
                                (e, "scraper", int(time.time())))
            stats["leads"] += len(batch)
            print(f"📥 {len(batch)} leads (total {stats['leads']})")
        await asyncio.sleep(0.1)

async def monitor():
    while True:
        await asyncio.sleep(30)
        print(f"📊 Scraping: pages={stats['pages']}, leads={stats['leads']}")

async def main():
    asyncio.create_task(storer())
    asyncio.create_task(monitor())
    for i in range(NB_AGENTS): asyncio.create_task(scraper(i, False))
    for i in range(NB_BOOSTERS): asyncio.create_task(scraper(i, True))
    await asyncio.Event().wait()

asyncio.run(main())
