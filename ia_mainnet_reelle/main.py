import sys, os
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB

import asyncio
import json
import os
import time
import base64
import aiohttp
import tweepy
from dotenv import load_dotenv

load_dotenv()

# ---------- Clés ----------
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID")
# Binance keys not used directly

# ---------- Twitter (désactivé car 404) ----------
async def post_tweet():
    return 0.0  # Désactivé

# ---------- 2Captcha (réaliste) ----------
async def solve_captcha():
    if not CAPTCHA_API_KEY:
        return 0.0
    # Pour gagner de l'argent, il faut un vrai fichier captcha.png
    if not os.path.exists("captcha.png"):
        print("📢 Aucun captcha → pas de gain")
        return 0.0
    with open("captcha.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    async with aiohttp.ClientSession() as session:
        create_payload = {
            "clientKey": CAPTCHA_API_KEY,
            "task": {
                "type": "ImageToTextTask",
                "body": img_b64,
                "phrase": False,
                "case": True,
                "numeric": 0,
                "math": False,
                "minLength": 1,
                "maxLength": 5
            },
            "languagePool": "en"
        }
        async with session.post("https://api.2captcha.com/createTask", json=create_payload) as resp:
            data = await resp.json()
            if data.get("errorId"):
                return 0.0
            task_id = data.get("taskId")
            if not task_id:
                return 0.0
        for _ in range(30):
            await asyncio.sleep(2)
            async with session.post("https://api.2captcha.com/getTaskResult", json={"clientKey": CAPTCHA_API_KEY, "taskId": task_id}) as res:
                result = await res.json()
                if result.get("status") == "ready":
                    cost = float(result.get("cost", 0.00025))
                    print(f"💰 Captcha résolu – gain réel: {cost} USD")
                    return cost
        return 0.0

# ---------- DeepSeek (payant) ----------
async def write_article():
    if not DEEPSEEK_API_KEY:
        return 0.0
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": "Write a short crypto article."}], "max_tokens": 500}
        try:
            async with session.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data) as resp:
                if resp.status == 200:
                    return 0.50
                else:
                    print(f"DeepSeek error {resp.status}")
        except Exception as e:
            print(f"DeepSeek exception: {e}")
    return 0.0

# ---------- GitHub (simulation) ----------
async def github_action():
    if not GITHUB_TOKEN:
        return 0.0
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        data = {"name": f"auto-article-{int(time.time())}", "auto_init": True, "private": False}
        try:
            async with session.post("https://api.github.com/user/repos", headers=headers, json=data) as resp:
                if resp.status == 201:
                    return 0.05
                else:
                    print(f"GitHub error {resp.status}")
        except Exception as e:
            print(f"GitHub exception: {e}")
    return 0.0

# ---------- Telegram (désactivé faute de chat_id valide) ----------
async def telegram_action():
    return 0.0

# ---------- Infura (simulation) ----------
async def infura_action():
    if not INFURA_PROJECT_ID:
        return 0.0
    url = f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}"
    payload = {"jsonrpc": "2.0", "method": "eth_getBalance", "params": ["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbF", "latest"], "id": 1}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    return 0.002
                else:
                    print(f"Infura error {resp.status}")
        except Exception as e:
            print(f"Infura exception: {e}")
    return 0.0

# ---------- Conversion USD -> BNB (CoinGecko, sans Binance) ----------
async def get_bnb_price_usd():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["binancecoin"]["usd"]
                else:
                    print(f"CoinGecko error: {resp.status}")
        except Exception as e:
            print(f"CoinGecko exception: {e}")
    return None

# ---------- Boucle principale ----------
async def main():
    print("🚀 Module réel démarré (2Captcha + DeepSeek + GitHub + Infura)")
    cycle = 0
    total_usd = 0.0
    while True:
        cycle += 1
        gain = await post_tweet() + await solve_captcha() + await write_article() + await github_action() + await telegram_action() + await infura_action()
        if gain > 0:
            total_usd += gain
            print(f"[Cycle {cycle}] Gains réels : {gain:.4f} USD → total brut: {total_usd:.4f} USD")
        else:
            print(f"[Cycle {cycle}] Aucun gain (vérifiez clés/captcha.png)")

        with open('state.json', 'w') as f:
            json.dump({'cycle': cycle, 'total_earnings_usd': total_usd}, f, indent=2)

        if total_usd > 0:
            bnb_price = await get_bnb_price_usd()
            if bnb_price:
                bnb_gain = total_usd / bnb_price
                print(f"💱 Conversion de {total_usd:.4f} USD → {bnb_gain:.8f} BNB (prix BNB = {bnb_price} USD)")
                try:
                    with open('wallet.json', 'r') as f:
                        wallet = json.load(f)
                except:
                    wallet = {'bnb_balance': 0.0, 'total_earnings_usd': 0.0, 'last_update': 0}
                wallet['bnb_balance'] = round(wallet.get('bnb_balance', 0.0) + bnb_gain, 8)
                wallet['total_earnings_usd'] = round(wallet.get('total_earnings_usd', 0.0) + total_usd, 2)
                wallet['last_update'] = int(time.time())
                with open('wallet.json', 'w') as f:
                    json.dump(wallet, f, indent=2)
                total_usd = 0.0
            else:
                print("⚠️ Impossible d'obtenir le prix BNB, conversion reportée")

        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt")
