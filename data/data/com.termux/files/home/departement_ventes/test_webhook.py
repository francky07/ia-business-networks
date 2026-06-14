import asyncio
import aiohttp
import os

async def test():
    webhook = os.getenv("SELL_WEBHOOK", "https://webhook.site/1537712d-64fa-4f07-89a1-5db665270134")
    payload = {"type": "test", "items": ["test@example.com"], "timestamp": 123}
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook, json=payload) as resp:
            print(f"Status: {resp.status}")
            print(await resp.text())

asyncio.run(test())
