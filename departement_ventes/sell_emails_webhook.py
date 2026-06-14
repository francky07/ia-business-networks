#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import os

WEBHOOK_URL = "http://localhost:8000/webhook"
KEYS_FILE = os.path.expanduser("~/agence_kays/keys.json")

async def sell_emails():
    async with aiohttp.ClientSession() as session:
        try:
            with open(KEYS_FILE) as f:
                data = json.load(f)
                emails = data.get("emails", [])
        except:
            print("❌ Impossible de lire keys.json")
            return
        if not emails:
            print("📭 Aucun email à vendre")
            return
        payload = {"type": "email", "items": emails, "timestamp": asyncio.get_event_loop().time()}
        try:
            async with session.post(WEBHOOK_URL, json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    gain = result.get("gain", len(emails) * 0.01)
                    print(f"💰 Vente (webhook local) : {len(emails)} emails → {gain} USD")
                    data["emails"] = []
                    with open(KEYS_FILE, "w") as f:
                        json.dump(data, f, indent=2)
                else:
                    print(f"❌ Erreur webhook: {resp.status}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(sell_emails())
