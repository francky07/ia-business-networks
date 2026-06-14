            log(f"Ajustement du prix des emails: {prix_actuel} -> {nouveau_prix} USD", "ACTION")
            subprocess.run(f"sed -i 's/montant = nb \\* [0-9.]*/montant = nb * {nouveau_prix}/' ~/departement_ventes/sell_emails_paypal.py", shell=True)

    def strategic_cycle(self):
        context = self.get_context()
        stats = self.get_db_stats()
        self.predictor.update(stats)
        trend = self.predictor.trend()
        log(f"Tendance des revenus: {trend}, prédiction pour demain: {self.predictor.predict_revenue():.2f} USD", "INFO")
        action, probs = self.swarm.decide(context)
        self.last_action = action
        self.execute_action(action, context)
        reward = stats["daily_rev"] - self.predictor.predict_revenue()
        self.swarm.reward_action(action, max(-0.5, min(0.5, reward)), context)
        dead = self.virtual_bots.heartbeat()
        if dead > 10:
            log(f"Attention: {dead} bots virtuels morts", "WARNING")
        self.send_report(stats, context)

    def send_report(self, stats, context):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        msg = (f"🧠 CEO Ultra Report\n"
               f"📧 Stock: {stats['stock']} | Revenu jour: {stats['daily_rev']:.2f} USD\n"
               f"👥 Leads: {stats['leads']}\n"
               f"🤖 Bots réels: {self.get_bot_stats()['active']}/{self.get_bot_stats()['total']}\n"
               f"🖥️ Bots virtuels: {self.virtual_bots.get_stats()['active']}/{self.virtual_bots.get_stats()['total']}\n"
               f"📈 Tendance: {self.predictor.trend()} | Prévision: {self.predictor.predict_revenue():.2f} USD\n"
               f"🎯 Dernière action: {self.last_action}")
        try:
            import requests
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                          json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=3)
        except: pass

def main():
    log("🧠 CEO Consciousness ×100 – Version Ultra démarrée", "STRATEGIC")
    ceo = UltraCEO()
    last_cycle = 0
    while True:
        now = time.time()
        if now - last_cycle >= 600:
            ceo.strategic_cycle()
            last_cycle = now
        time.sleep(60)

if __name__ == "__main__":
    main()
EOF

tmux kill-session -t ceo_ultra 2>/dev/null
tmux new-session -d -s ceo_ultra "python ~/ia_nexus/ceo_consciousness_ultra.py"
echo "✅ CEO Ultra entièrement corrigé et relancé. Attachement dans 2 secondes..."
sleep 2
tmux attach -t ceo_ultra
cat > ~/ia_nexus/ceo_advanced.py << 'EOF'
#!/usr/bin/env python3
"""
CEO Advanced – Module de supervision avancée
- Analyse prédictive (régression polynomiale, détection de tendances)
- Gestion de crise (détection d’anomalies, plans de reprise)
- Planification stratégique (objectifs multi‑périodes)
- Tableau de bord HTML dynamique
- Alertes intelligentes (seuils adaptatifs)
"""
import os
import sys
import time
import sqlite3
import subprocess
import json
import random
import math
import webbrowser
from datetime import datetime, timedelta
from collections import deque
import numpy as np

sys.path.append(os.path.expanduser("~/ia_shared"))
try:
    from ia_nexus import ConfigManager
except ImportError:
    ConfigManager = type('ConfigManager', (), {'get': lambda self, k, d=None: os.getenv(k, d)})()

DB_PATH = os.path.expanduser("~/ia_shared/db/nexus.db")
LOG_FILE = os.path.expanduser("~/ceo_advanced.log")
DASHBOARD_HTML = os.path.expanduser("~/ceo_dashboard.html")
DECISIONS_FILE = os.path.expanduser("~/ceo_advanced_decisions.json")
TELEGRAM_BOT_TOKEN = ConfigManager.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = ConfigManager.get("TELEGRAM_CHAT_ID")

# ========== Utilitaires ==========
def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    if level in ("CRITICAL", "ERROR", "CRISIS", "STRATEGIC") and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            import requests
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                          json={"chat_id": TELEGRAM_CHAT_ID, "text": f"🧠 CEO: {msg}"}, timeout=3)
        except: pass

def save_decision(decision, context):
    try:
        with open(DECISIONS_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append({"timestamp": datetime.now().isoformat(), "decision": decision, "context": context})
    if len(data) > 500:
        data = data[-500:]
    with open(DECISIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ========== Analyse prédictive avancée ==========
class AdvancedPredictor:
    def __init__(self, window=48):
        self.revenue_history = deque(maxlen=window)
        self.stock_history = deque(maxlen=window)
        self.lead_history = deque(maxlen=window)
        self.model = None

    def update(self, stats):
        self.revenue_history.append(stats["daily_rev"])
        self.stock_history.append(stats["stock"])
        self.lead_history.append(stats["leads"])

    def polynomial_trend(self, data, degree=2):
        if len(data) < degree+1:
            return 0
        x = np.arange(len(data))
        y = np.array(data)
        coeffs = np.polyfit(x, y, degree)
        poly = np.poly1d(coeffs)
        return poly(len(data))  # prédiction du prochain point

    def predict_revenue(self):
        if len(self.revenue_history) < 5:
            return 0
        try:
            return max(0, self.polynomial_trend(self.revenue_history, degree=2))
        except:
            return self.revenue_history[-1] if self.revenue_history else 0

    def detect_anomaly(self):
        if len(self.revenue_history) < 7:
            return False
        mean = np.mean(self.revenue_history)
        std = np.std(self.revenue_history)
        last = self.revenue_history[-1]
        return abs(last - mean) > 2*std

    def trend(self):
        if len(self.revenue_history) < 3:
            return "stable"
        # Pente des 3 derniers points
        slope = self.revenue_history[-1] - self.revenue_history[-3]
        if slope > 0.5:
            return "hausse"
        elif slope < -0.5:
            return "baisse"
        else:
            return "stable"

# ========== Gestion de crise ==========
class CrisisManager:
    def __init__(self):
        self.crisis_mode = False
        self.crisis_start = None
        self.recovery_plan = None

    def detect_crisis(self, stats, predictor):
        # Critères de crise
        if stats["stock"] > 5000:
            log("⚠️ Crise: stock excessif (>5000)", "CRISIS")
            return True
        if predictor.detect_anomaly():
            log("⚠️ Crise: anomalie détectée (chute brutale des revenus)", "CRISIS")
            return True
        if len([b for b in subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout.splitlines() if b]) < 10:
            log("⚠️ Crise: moins de 10 bots actifs", "CRISIS")
            return True
        return False

    def activate_crisis_mode(self, stats):
        self.crisis_mode = True
        self.crisis_start = datetime.now()
        # Plan de reprise : liquidation massive, recrutement d'urgence
        log("🔴 ACTIVATION DU PLAN DE CRISE", "CRISIS")
        # Vider le stock en urgence (vente à prix cassé)
        subprocess.run(["sed", "-i", "s/montant = nb \\* [0-9.]*/montant = nb * 0.002/", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
        log("Prix réduit à 0.002 USD par email pour liquidation", "CRISIS")
        # Recruter des bots supplémentaires (relance)
        subprocess.run(["tmux", "new-session", "-d", "-s", "crisis_booster", "python ~/ia_booster_pro.py"], capture_output=True)
        self.recovery_plan = "Liquidation du stock + recrutement d'urgence"

    def recover(self):
        if self.crisis_mode and (datetime.now() - self.crisis_start).seconds > 3600:
            log("✅ Fin de la crise – retour à la normale", "CRISIS")
            # Restaurer les prix normaux
            subprocess.run(["sed", "-i", "s/montant = nb \\* 0.002/montant = nb * 0.01/", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")])
            self.crisis_mode = False
            self.crisis_start = None
            self.recovery_plan = None

# ========== Planification stratégique ==========
class StrategicPlanner:
    def __init__(self):
        self.objectives = {
            "short_term": {"revenue_target": 5.0, "stock_target": 1000},
            "medium_term": {"revenue_target": 50.0, "leads_target": 500},
            "long_term": {"revenue_target": 500.0, "market_share": 0.05}
        }
        self.plan = []

    def evaluate(self, stats):
        short_revenue_ok = stats["daily_rev"] >= self.objectives["short_term"]["revenue_target"]
        short_stock_ok = stats["stock"] <= self.objectives["short_term"]["stock_target"]
        if not short_revenue_ok:
            log("Objectif court terme : augmentation des revenus nécessaire", "STRATEGIC")
            # Proposition : lancer une campagne marketing
            return "marketing"
        if not short_stock_ok:
            log("Objectif court terme : stock trop élevé, accélérer les ventes", "STRATEGIC")
            return "vente_acceleree"
        return None

    def generate_plan(self):
        self.plan = [
            {"action": "increase_price", "condition": "stock < 100", "effect": "augmenter prix à 0.02"},
            {"action": "decrease_price", "condition": "stock > 2000", "effect": "baisser prix à 0.005"},
            {"action": "hire_agents", "condition": "bots_actifs < 15", "effect": "lancer nouveaux boosters"},
        ]
        log("Plan stratégique généré", "STRATEGIC")

# ========== Tableau de bord HTML ==========
def generate_dashboard(stats, bot_stats, predictor, crisis_mode):
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>CEO Dashboard</title>
<style>
body {{font-family: Arial; margin: 20px; background: #f0f0f0;}}
.container {{max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px;}}
h1 {{color: #2c3e50;}}
.metric {{display: inline-block; width: 200px; margin: 10px; padding: 10px; background: #e8f4f8; border-radius: 5px;}}
.crisis {{background: #ffcccc; padding: 10px; border-left: 5px solid red;}}
table {{width: 100%; border-collapse: collapse;}}
th, td {{border: 1px solid #ddd; padding: 8px; text-align: left;}}
th {{background-color: #f2f2f2;}}
</style>
</head>
<body>
<div class="container">
<h1>🧠 CEO Advanced Dashboard</h1>
<p>Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<div class="metric">📧 Stock emails : {stats['stock']}</div>
<div class="metric">💰 Revenu jour : {stats['daily_rev']:.2f} USD</div>
<div class="metric">👥 Leads : {stats['leads']}</div>
<div class="metric">🤖 Bots actifs : {bot_stats['active']}/{bot_stats['total']}</div>
<div class="metric">📈 Tendance : {predictor.trend()}</div>
<div class="metric">🔮 Prédiction demain : {predictor.predict_revenue():.2f} USD</div>
{f'<div class="metric crisis">🚨 MODE CRISE ACTIF</div>' if crisis_mode else ''}
<h2>Dernières décisions</h2>
<table>
<tr><th>Heure</th><th>Décision</th><th>Contexte</th></tr>
"""
    try:
        with open(DECISIONS_FILE, "r") as f:
            decisions = json.load(f)
        for d in decisions[-10:]:
            html += f"<tr><td>{d['timestamp'][:19]}</td><td>{d['decision']}</td><td>{str(d['context'])[:50]}</td></tr>"
    except:
        pass
    html += """
</table>
</div>
</body>
</html>"""
    with open(DASHBOARD_HTML, "w") as f:
        f.write(html)
    log("Tableau de bord HTML mis à jour", "INFO")

# ========== CEO Advanced ==========
class CEOAdvanced:
    def __init__(self):
        self.predictor = AdvancedPredictor()
        self.crisis_mgr = CrisisManager()
        self.planner = StrategicPlanner()
        self.planner.generate_plan()
        self.last_dashboard = 0

    def get_db_stats(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0")
            stock = c.fetchone()[0]
            c.execute("SELECT COALESCE(SUM(montant),0) FROM ventes")
            revenue = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM leads")
            leads = c.fetchone()[0]
            c.execute("SELECT COALESCE(SUM(montant),0) FROM ventes WHERE date > strftime('%s','now','-1 day')")
            daily_rev = c.fetchone()[0]
            conn.close()
            return {"stock": stock, "revenue": revenue, "leads": leads, "daily_rev": daily_rev}
        except:
            return {"stock": 0, "revenue": 0, "leads": 0, "daily_rev": 0}

    def get_bot_stats(self):
        expected = ["agence_kays", "ventes", "ia_net", "booster", "booster_pro", "hub", "hub_client",
                    "opp_auto", "ia_reelle", "oeil_de_dieu", "healing", "finance", "finance_booster",
                    "cerebrum", "nexus_brain", "booster_agence", "app_auto", "prospector_ultra",
                    "paypal_scanner", "nexus_dashboard", "brain_sim", "ceo_advanced"]
        active_out = subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout
        active_names = [line.split(":")[0] for line in active_out.splitlines() if line]
        missing = [b for b in expected if b not in active_names]
        return {"active": len(active_names), "missing": missing, "total": len(expected)}

    def strategic_cycle(self):
        stats = self.get_db_stats()
        self.predictor.update(stats)
        bot_stats = self.get_bot_stats()
        # Détection de crise
        if self.crisis_mgr.detect_crisis(stats, self.predictor):
            if not self.crisis_mgr.crisis_mode:
                self.crisis_mgr.activate_crisis_mode(stats)
        else:
            self.crisis_mgr.recover()
        # Planification
        action = self.planner.evaluate(stats)
        if action == "marketing":
            log("🔊 Lancement d'une campagne marketing (simulation)", "STRATEGIC")
        elif action == "vente_acceleree":
            log("⚡ Accélération des ventes (déclenchement manuel)", "STRATEGIC")
            subprocess.run(["python", os.path.expanduser("~/departement_ventes/sell_emails_paypal.py")], capture_output=True)
        # Mise à jour du dashboard HTML (toutes les 5 minutes)
        now = time.time()
        if now - self.last_dashboard > 300:
            generate_dashboard(stats, bot_stats, self.predictor, self.crisis_mgr.crisis_mode)
            self.last_dashboard = now
        # Envoi du rapport toutes les heures
        if int(now) % 3600 < 60:
            self.send_telegram_report(stats, bot_stats)

    def send_telegram_report(self, stats, bot_stats):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        msg = (f"🧠 CEO Advanced Report\n"
               f"📧 Stock: {stats['stock']} | Revenu jour: {stats['daily_rev']:.2f} USD\n"
               f"👥 Leads: {stats['leads']} | 🤖 Bots: {bot_stats['active']}/{bot_stats['total']}\n"
               f"📈 Tendance: {self.predictor.trend()} | 🔮 Prédiction: {self.predictor.predict_revenue():.2f} USD\n"
               f"🚨 Mode crise: {'OUI' if self.crisis_mgr.crisis_mode else 'NON'}")
        try:
            import requests
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                          json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=3)
        except: pass

def main():
    log("🧠 CEO Advanced – Module de supervision avancée démarré", "STRATEGIC")
    ceo = CEOAdvanced()
    while True:
        ceo.strategic_cycle()
        time.sleep(60)  # cycle toutes les minutes

if __name__ == "__main__":
    main()
EOF

tmux kill-session -t ceo_advanced 2>/dev/null
tmux new-session -d -s ceo_advanced "python ~/ia_nexus/ceo_advanced.py"
echo "✅ CEO Advanced installé et lancé (session 'ceo_advanced')"
echo "📌 Logs: tail -f ~/ceo_advanced.log"
echo "📌 Tableau de bord HTML: ~/ceo_dashboard.html (ouvrez-le dans un navigateur)"
echo "📌 Le module détecte les crises, planifie des actions, génère un dashboard visuel et envoie des rapports Telegram."
pkill crond 2>/dev/null; rm -f /data/data/com.termux/files/usr/var/run/crond.pid; tmux kill-server 2>/dev/null; sleep 2; cd ~; [ -f ~/agence_kays/agence.py ] && tmux new-session -d -s agence_kays "python ~/agence_kays/agence.py"; [ -f ~/departement_ventes/ventes.py ] && tmux new-session -d -s ventes "cd ~/departement_ventes && python ventes.py"; [ -f ~/ia_net_pro.py ] && tmux new-session -d -s ia_net "python ~/ia_net_pro.py"; [ -f ~/ia_booster_pro.py ] && tmux new-session -d -s booster "python ~/ia_booster_pro.py"; [ -f ~/ia_booster_pro_250.py ] && tmux new-session -d -s booster_pro "python ~/ia_booster_pro_250.py"; [ -f ~/ia_booster_agence.py ] && tmux new-session -d -s booster_agence "python ~/ia_booster_agence.py"; [ -f ~/ia_hub_advanced.py ] && tmux new-session -d -s hub "python ~/ia_hub_advanced.py"; [ -f ~/hub_client_advanced.py ] && tmux new-session -d -s hub_client "python ~/hub_client_advanced.py"; [ -f ~/ia_opp_autonomous.py ] && tmux new-session -d -s opp_auto "python ~/ia_opp_autonomous.py"; [ -d ~/ia_mainnet_reelle ] && [ -f ~/ia_mainnet_reelle/main.py ] && (cd ~/ia_mainnet_reelle && tmux new-session -d -s ia_reelle "python main.py"); [ -f ~/oeil_de_dieu/oeil_de_dieu.py ] && tmux new-session -d -s oeil_de_dieu "python ~/oeil_de_dieu/oeil_de_dieu.py"; [ -f ~/self_healing.py ] && tmux new-session -d -s healing "python ~/self_healing.py"; [ -f ~/ia_finance_500.py ] && tmux new-session -d -s finance "python ~/ia_finance_500.py"; [ -f ~/ia_finance_booster_500.py ] && tmux new-session -d -s finance_booster "python ~/ia_finance_booster_500.py"; [ -f ~/cerebrum/brain/cerebrum_maximus.py ] && tmux new-session -d -s cerebrum "cd ~/cerebrum/brain && python cerebrum_maximus.py"; [ -f ~/ia_nexus/core/nexus_brain.py ] && tmux new-session -d -s nexus_brain "cd ~/ia_nexus && python core/nexus_brain.py"; [ -f ~/app_auto.py ] && tmux new-session -d -s app_auto "python ~/app_auto.py"; [ -f ~/ia_nexus/prospector_ultra.py ] && tmux new-session -d -s prospector_ultra "python ~/ia_nexus/prospector_ultra.py"; [ -f ~/scan_paypal_payments.py ] && tmux new-session -d -s paypal_scanner "while true; do python ~/scan_paypal_payments.py; sleep 120; done"; [ -f ~/dashboard_nexus.sh ] && tmux new-session -d -s nexus_dashboard "bash ~/dashboard_nexus.sh"; [ -f ~/brain_simulation.py ] && tmux new-session -d -s brain_sim "python ~/brain_simulation.py"; [ -f ~/ia_nexus/ceo_consciousness_ultra.py ] && tmux new-session -d -s ceo_ultra "python ~/ia_nexus/ceo_consciousness_ultra.py"; [ -f ~/ia_nexus/ceo_advanced.py ] && tmux new-session -d -s ceo_advanced "python ~/ia_nexus/ceo_advanced.py"; [ -f ~/watch_main_logs.sh ] && tmux new-session -d -s main_logs "~/watch_main_logs.sh"; echo "✅ Redémarrage complet effectué" && tmux ls
#!/bin/bash
set -e
echo "════════════════════════════════════════════════════════════════"
echo "  🚀 INSTALLATION COMPLÈTE – IA BUSINESS (tous modules)"
echo "════════════════════════════════════════════════════════════════"
# 1. Mise à jour et dépendances
pkg update -y && pkg upgrade -y
pkg install -y python tmux sqlite git curl wget jq nano
pip install --upgrade pip
#!/bin/bash
set -e
echo "════════════════════════════════════════════════════════════════"
echo "  🚀 INSTALLATION COMPLÈTE – IA BUSINESS (tous modules)"
echo "════════════════════════════════════════════════════════════════"
# 1. Mise à jour et dépendances
pkg update -y && pkg upgrade -y
pkg install -y python tmux sqlite git curl wget jq nano
pip install --upgrade pip
tail -f ~/ia_ceo_state/ceo_ultra_stable.log
sed -i 's|https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT|https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd|' ~/ia_nexus/ceo_ultra_stable.py && sed -i 's/resp.json()\["price"\]/resp.json()\["binancecoin"\]\["usd"\]/' ~/ia_nexus/ceo_ultra_stable.py && tmux kill-session -t ceo_ultra 2>/dev/null && tmux new-session -d -s ceo_ultra "python ~/ia_nexus/ceo_ultra_stable.py" && echo "✅ CEO redémarré avec API CoinGecko pour le taux BNB" && tail -f ~/ia_ceo_state/ceo_ultra_stable.log
tmux kill-server 2>/dev/null; sleep 2; cd ~; [ -f ~/agence_kays/agence.py ] && tmux new-session -d -s agence_kays "python ~/agence_kays/agence.py"; [ -f ~/departement_ventes/ventes.py ] && tmux new-session -d -s ventes "cd ~/departement_ventes && python ventes.py"; [ -f ~/ia_net_pro.py ] && tmux new-session -d -s ia_net "python ~/ia_net_pro.py"; [ -f ~/ia_booster_pro.py ] && tmux new-session -d -s booster "python ~/ia_booster_pro.py"; [ -f ~/ia_booster_pro_250.py ] && tmux new-session -d -s booster_pro "python ~/ia_booster_pro_250.py"; [ -f ~/ia_booster_agence.py ] && tmux new-session -d -s booster_agence "python ~/ia_booster_agence.py"; [ -f ~/ia_hub_advanced.py ] && tmux new-session -d -s hub "python ~/ia_hub_advanced.py"; [ -f ~/hub_client_advanced.py ] && tmux new-session -d -s hub_client "python ~/hub_client_advanced.py"; [ -f ~/ia_opp_autonomous.py ] && tmux new-session -d -s opp_auto "python ~/ia_opp_autonomous.py"; [ -d ~/ia_mainnet_reelle ] && [ -f ~/ia_mainnet_reelle/main.py ] && (cd ~/ia_mainnet_reelle && tmux new-session -d -s ia_reelle "python main.py"); [ -f ~/oeil_de_dieu/oeil_de_dieu.py ] && tmux new-session -d -s oeil_de_dieu "python ~/oeil_de_dieu/oeil_de_dieu.py"; [ -f ~/self_healing.py ] && tmux new-session -d -s healing "python ~/self_healing.py"; [ -f ~/ia_finance_500.py ] && tmux new-session -d -s finance "python ~/ia_finance_500.py"; [ -f ~/ia_finance_booster_500.py ] && tmux new-session -d -s finance_booster "python ~/ia_finance_booster_500.py"; [ -f ~/cerebrum/brain/cerebrum_maximus.py ] && tmux new-session -d -s cerebrum "cd ~/cerebrum/brain && python cerebrum_maximus.py"; [ -f ~/ia_nexus/core/nexus_brain.py ] && tmux new-session -d -s nexus_brain "cd ~/ia_nexus && python core/nexus_brain.py"; [ -f ~/app_auto.py ] && tmux new-session -d -s app_auto "python ~/app_auto.py"; [ -f ~/ia_nexus/scrapers/mega_scraper.py ] && tmux new-session -d -s mega_scraper "python ~/ia_nexus/scrapers/mega_scraper.py"; [ -f ~/scan_paypal_payments.py ] && tmux new-session -d -s paypal_scanner "while true; do python ~/scan_paypal_payments.py; sleep 120; done"; [ -f ~/ia_nexus/ceo_ultra_stable.py ] && tmux new-session -d -s ceo_ultra "python ~/ia_nexus/ceo_ultra_stable.py"; [ -f ~/dashboard_nexus.sh ] && tmux new-session -d -s nexus_dashboard "bash ~/dashboard_nexus.sh"; [ -f ~/brain_simulation.py ] && tmux new-session -d -s brain_sim "python ~/brain_simulation.py"; [ -f ~/watch_main_logs.sh ] && tmux new-session -d -s main_logs "~/watch_main_logs.sh"; echo "✅ Redémarrage complet effectué" && tmux ls
exit
# Session 1 : production
tmux new-session -d -s prod
tmux send-keys -t prod "cd ~ && python agence_kays/agence.py &" C-m
tmux send-keys -t prod "cd ~/departement_ventes && python ventes.py &" C-m
tmux send-keys -t prod "python ia_net_pro.py" C-m
exit
python ia_booster_pro.py &
python ia_booster_pro_250.py &
python ia_booster_agence.py &
python ia_nexus/mega_booster_1000.py &
python self_healing.py &
python oeil_de_dieu/oeil_de_dieu.py
cd ~/cerebrum/brain && python cerebrum_maximus.py &
cd ~/ia_nexus && python core/nexus_brain.py &
python ia_nexus/ceo_unified.py &
python ia_nexus/ceo_neuronal_booster.py &
python brain_simulation.py &
bash dashboard_nexus.sh
cd ~ && python agence_kays/agence.py &
cd ~/departement_ventes && python ventes.py &
python ia_net_pro.py
python ia_hub_advanced.py &
python hub_client_advanced.py &
python ia_opp_autonomous.py &
while true; do python scan_paypal_payments.py; sleep 120; done &
python app_auto.py
python ia_booster_pro.py &
python ia_booster_pro_250.py &
python ia_booster_agence.py &
python ia_nexus/mega_booster_1000.py &
python self_healing.py &
python oeil_de_dieu/oeil_de_dieu.py
cd ~/cerebrum/brain && python cerebrum_maximus.py &
cd ~/ia_nexus && python core/nexus_brain.py &
python ia_nexus/ceo_unified.py &
python ia_nexus/ceo_neuronal_booster.py &
python brain_simulation.py &
bash dashboard_nexus.sh
python ia_hub_advanced.py &
python hub_client_advanced.py &
python ia_opp_autonomous.py &
while true; do python scan_paypal_payments.py; sleep 120; done &
python app_auto.py
cd ~ && python agence_kays/agence.py &
cd ~/departement_ventes && python ventes.py &
python ia_net_pro.py
cd ~ && python agence_kays/agence.py &
cd ~/departement_ventes && python ventes.py &
python ia_net_pro.py
python ia_booster_pro.py &
python ia_booster_pro_250.py &
python ia_booster_agence.py &
python ia_nexus/mega_booster_1000.py &
python self_healing.py &
python oeil_de_dieu/oeil_de_dieu.py
python ia_hub_advanced.py &
python hub_client_advanced.py &
python ia_opp_autonomous.py &
while true; do python scan_paypal_payments.py; sleep 120; done &
python app_auto.py
cd ~/cerebrum/brain && python cerebrum_maximus.py &
cd ~/ia_nexus && python core/nexus_brain.py &
python ia_nexus/ceo_unified.py &
python ia_nexus/ceo_neuronal_booster.py &
python brain_simulation.py &
bash dashboard_nexus.sh
cd ~ && python agence_kays/agence.py &
cd ~/departement_ventes && python ventes.py &
python ia_net_pro.py
exit
tmux attach -t prod     # production
exit
tmux is
exit
python ia_booster_pro.py &
python ia_booster_pro_250.py &
python ia_booster_agence.py &
python ia_nexus/mega_booster_1000.py &
python self_healing.py &
python oeil_de_dieu/oeil_de_dieu.py
python ia_hub_advanced.py &
python hub_client_advanced.py &
python ia_opp_autonomous.py &
while true; do python scan_paypal_payments.py; sleep 120; done &
python app_auto.py
cd ~/cerebrum/brain && python cerebrum_maximus.py &
cd ~/ia_nexus && python core/nexus_brain.py &
python ia_nexus/ceo_unified.py &
python ia_nexus/ceo_neuronal_booster.py &
python brain_simulation.py &
bash dashboard_nexus.sh
# Créer le fichier log partagé et rediriger la sortie du pane
tmux pipe-pane -t ceo_unified -o "cat >> ~/ceo_shared.log"
# Créer une session mirror qui affiche ce fichier
tmux new-session -d -s mirror_ceo "tail -f ~/ceo_shared.log"
echo "✅ Mirror créé. Attachez-vous avec : tmux attach -t mirror_ceo"
tar -czf ~/backup_ia_business_complete_$(date +%Y%m%d_%H%M%S).tar.gz     --exclude="*.log"     --exclude="*.pyc"     --exclude="__pycache__"     --exclude="*.db-journal"     --exclude="backup_*"     --exclude="ceo_*.log"     ~/agence_kays     ~/departement_ventes     ~/ia_nexus     ~/cerebrum     ~/ia_shared     ~/ia_mainnet_reelle     ~/oeil_de_dieu     ~/ia_net_pro.py     ~/ia_booster_pro.py     ~/ia_booster_pro_250.py     ~/ia_hub_advanced.py     ~/hub_client_advanced.py     ~/ia_opp_autonomous.py     ~/self_healing.py     ~/ia_finance_500.py     ~/ia_finance_booster_500.py     ~/app_auto.py     ~/dashboard_nexus.sh     ~/brain_simulation.py     ~/watch_main_logs.sh     ~/minimal_dashboard.sh     ~/watch_ceo_final.sh     ~/scan_paypal_payments.py     ~/.env_ia_business \
exot
exit
