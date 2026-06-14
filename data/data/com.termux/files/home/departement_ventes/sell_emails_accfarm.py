#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import os

ACCFARM_EMAIL = "seckndananeuh@gmail.com"
ACCFARM_PASSWORD = "SaintLouis65#"
KEYS_FILE = os.path.expanduser("~/agence_kays/keys.json")

async def get_bearer_token(session):
    url = "https://accfarm.com/api/v1/user/login"
    payload = {"email": ACCFARM_EMAIL, "password": ACCFARM_PASSWORD}
    async with session.post(url, json=payload) as resp:
        if resp.status == 200:
            data = await resp.json()
            return data.get("bearerToken"), data.get("userSecret")
        else:
            print(f"❌ Échec auth: {resp.status} - {await resp.text()}")
            return None, None

async def sell_emails():
    async with aiohttp.ClientSession() as session:
        token, secret = await get_bearer_token(session)
        if not token:
            return
        # Lire les emails depuis keys.json
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
        # Vente via l'API Accfarm
        url = "https://accfarm.com/api/v1/sell"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "emails": emails,
            "price_per_unit": 0.01   # 0.01 $ par email
        }
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                gain = result.get("total", len(emails) * 0.01)
                print(f"💰 Vente réussie : {len(emails)} emails → {gain} USD")
                # Vider la liste des emails après vente
                data["emails"] = []
                with open(KEYS_FILE, "w") as f:
                    json.dump(data, f, indent=2)
            else:
                print(f"❌ Erreur vente: {resp.status} - {await resp.text()}")

if __name__ == "__main__":
    asyncio.run(sell_emails())
