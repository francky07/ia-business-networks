#!/data/data/com.termux/files/usr/bin/bash
# Surveillance du booster IA NetSolutions PRO - Version corrigée
clear
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   IA NetSolutions PRO - BOOSTER                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
date
echo ""

echo "📌 BOOSTER (dernières 15 lignes) :"
tmux capture-pane -pt booster -S -15 2>/dev/null | tail -15 || echo "   Session booster introuvable"
echo ""

echo "🛡️ ÉTAT DES SERVICES (depuis booster)"
# Extraction correcte du token GitHub (cherche la ligne GITHUB_TOKEN = "...")
TOKEN=$(grep -E '^GITHUB_TOKEN = "' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
if [ -n "$TOKEN" ]; then
    if curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null 2>&1; then
        echo "   🐙 GitHub : ✅ (token valide)"
    else
        echo "   🐙 GitHub : ❌ (token invalide)"
    fi
else
    echo "   🐙 GitHub : ⚠️ token manquant"
fi
echo ""

echo "⛓️ BINANCE SMART CHAIN"
if python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); exit(0 if w3.is_connected() else 1)" 2>/dev/null; then
    BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(bal)" 2>/dev/null)
    echo "   ✅ Connecté – Solde BNB: $BAL"
else
    echo "   ❌ Déconnecté"
fi
echo ""

echo "🖥️ PROCESSUS"
pgrep -f "ia_booster_pro.py" > /dev/null && echo "   ✅ Booster : actif (PID: $(pgrep -f ia_booster_pro.py | tr '\n' ' '))" || echo "   ❌ Booster : arrêté"
pgrep -f "ia_net_pro.py" > /dev/null && echo "   ✅ Bot principal : actif" || echo "   ❌ Bot principal : arrêté"
echo ""

echo "🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter)"
