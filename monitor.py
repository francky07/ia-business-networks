#!/usr/bin/env python3
import time, subprocess, requests, os, sys, re
from datetime import datetime

def log(msg): print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def check_github():
    # Lit le token dans ia_net.py
    token = None
    try:
        with open('ia_net.py', 'r') as f:
            for line in f:
                if line.startswith('GITHUB_TOKEN'):
                    token = line.split('=')[1].strip().strip('"')
                    break
    except: pass
    if not token:
        log("⚠️ GitHub: token manquant")
        return False
    headers = {"Authorization": f"token {token}"}
    try:
        r = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if r.status_code == 200:
            log("✅ GitHub OK")
            return True
        else:
            log(f"❌ GitHub: {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ GitHub erreur: {e}")
        return False

def check_openai():
    key = None
    try:
        with open('ia_net.py', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY'):
                    key = line.split('=')[1].strip().strip('"')
                    break
    except: pass
    if not key or key == "":
        log("ℹ️ OpenAI: non configuré")
        return "not_configured"
    headers = {"Authorization": f"Bearer {key}"}
    try:
        r = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        if r.status_code == 200:
            # Test de quota
            data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1}
            r2 = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
            if r2.status_code == 429:
                log("⚠️ OpenAI: quota épuisé")
                return "quota_exceeded"
            else:
                log("✅ OpenAI OK")
                return True
        else:
            log(f"❌ OpenAI: {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ OpenAI erreur: {e}")
        return False

def check_telegram():
    bot_token = None
    try:
        with open('ia_net.py', 'r') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN'):
                    bot_token = line.split('=')[1].strip().strip('"')
                    break
    except: pass
    if not bot_token or bot_token == "":
        log("ℹ️ Telegram: non configuré")
        return "not_configured"
    try:
        r = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        if r.status_code == 200:
            log("✅ Telegram OK")
            return True
        else:
            log(f"❌ Telegram: {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ Telegram erreur: {e}")
        return False

def check_bot():
    # Vérifie si le processus python ia_net.py tourne
    result = subprocess.run("pgrep -f 'python.*ia_net.py'", shell=True, capture_output=True)
    if result.returncode == 0:
        log("✅ Bot IA actif")
        return True
    else:
        log("❌ Bot IA arrêté")
        return False

def restart_bot():
    log("🔁 Redémarrage du bot IA...")
    subprocess.run("tmux kill-session -t ia_net 2>/dev/null; ./start_ia.sh", shell=True)
    time.sleep(5)

def check_tor():
    # Vérifie si Tor tourne
    result = subprocess.run("pgrep tor", shell=True, capture_output=True)
    if result.returncode == 0:
        return True
    return False

def restart_tor():
    log("🔁 Redémarrage de Tor...")
    subprocess.run("pkill tor; tor &", shell=True)
    time.sleep(3)

def main():
    log("🚀 Lancement du module de surveillance (cycle 60s)")
    while True:
        # 1. Vérifier et réparer Tor
        if not check_tor():
            log("⚠️ Tor arrêté – redémarrage")
            restart_tor()
        # 2. GitHub
        if not check_github():
            log("⚠️ GitHub en échec – le bot pourra toujours générer le blog localement")
        # 3. OpenAI
        oai = check_openai()
        if oai == "quota_exceeded":
            log("⚠️ Quota OpenAI épuisé – rechargez vos crédits")
        # 4. Telegram
        tg = check_telegram()
        # 5. Bot principal
        if not check_bot():
            restart_bot()
        time.sleep(60)

if __name__ == "__main__":
    main()
