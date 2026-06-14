#!/data/data/com.termux/files/usr/bin/bash
# IA NetSolutions PRO - Diagnostic et auto-dépannage
set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     IA NetSolutions PRO - Diagnostic & Auto-dépannage             ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
date

# ---------- 1. Vérification des processus ----------
echo ""
echo "🔍 1. PROCESSUS ACTIFS"
ps aux | grep -E "ia_net_pro.py|ia_pi_agents.py|ia_booster_pro.py|pi_backend.py" | grep -v grep || echo "   Aucun processus IA trouvé"

# ---------- 2. Vérification des sessions tmux ----------
echo ""
echo "📺 2. SESSIONS TMUX"
if tmux ls 2>/dev/null; then
    echo "   Sessions existantes"
else
    echo "   ❌ Aucune session tmux"
fi

# ---------- 3. Vérification du fichier mémoire ----------
echo ""
echo "💾 3. FICHIER MÉMOIRE (ia_mem_pro.json)"
if [ -f ia_mem_pro.json ]; then
    if python -c "import json; json.load(open('ia_mem_pro.json'))" 2>/dev/null; then
        echo "   ✅ Fichier valide"
    else
        echo "   ❌ Fichier corrompu → recréation"
        rm -f ia_mem_pro.json
        echo '{"stats":{"cycle":0,"actions":0},"errors":[],"last_balance":0.0}' > ia_mem_pro.json
        echo "   ✅ Fichier recréé"
    fi
else
    echo "   ⚠️ Fichier absent → création"
    echo '{"stats":{"cycle":0,"actions":0},"errors":[],"last_balance":0.0}' > ia_mem_pro.json
    echo "   ✅ Fichier créé"
fi

# ---------- 4. Vérification des clés API ----------
echo ""
echo "🔑 4. CONFIGURATION DES CLÉS"
# GitHub
if grep -q '^GITHUB_TOKEN = ""' ia_net_pro.py; then
    echo "   ⚠️ Token GitHub manquant (nécessaire pour déploiement)"
else
    TOKEN=$(grep '^GITHUB_TOKEN' ia_net_pro.py | cut -d'"' -f2)
    if curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null; then
        echo "   🐙 GitHub : ✅"
    else
        echo "   🐙 GitHub : ❌ token invalide"
    fi
fi
# Telegram
if grep -q '^TELEGRAM_BOT_TOKEN = ""' ia_net_pro.py; then
    echo "   📡 Telegram : ⚠️ non configuré"
else
    BOT=$(grep '^TELEGRAM_BOT_TOKEN' ia_net_pro.py | cut -d'"' -f2)
    if curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true'; then
        echo "   📡 Telegram : ✅"
    else
        echo "   📡 Telegram : ❌ token invalide"
    fi
fi
# OpenAI
if grep -q '^OPENAI_API_KEY = ""' ia_net_pro.py; then
    echo "   🤖 OpenAI : ⚠️ non configuré"
else
    KEY=$(grep '^OPENAI_API_KEY' ia_net_pro.py | cut -d'"' -f2)
    if curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null; then
        echo "   🤖 OpenAI : ✅"
    else
        echo "   🤖 OpenAI : ❌ clé invalide/quota"
    fi
fi
# Infura et Pi (fichier .env)
if [ -f ~/ia_web/.env ]; then
    INFURA_KEY=$(grep '^INFURA_KEY=' ~/ia_web/.env | cut -d'=' -f2)
    if [ -n "$INFURA_KEY" ]; then
        python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/$INFURA_KEY')); exit(0 if w3.is_connected() else 1)" 2>/dev/null && echo "   🔌 Infura : ✅" || echo "   🔌 Infura : ❌"
    else
        echo "   🔌 Infura : ⚠️ clé manquante"
    fi
    PI_KEY=$(grep '^PI_API_KEY=' ~/ia_web/.env | cut -d'=' -f2)
    if [ -n "$PI_KEY" ]; then
        curl -s -H "Authorization: Key $PI_KEY" https://api.minepi.com/v2/me > /dev/null && echo "   🥧 Pi Network : ✅" || echo "   🥧 Pi Network : ❌"
    else
        echo "   🥧 Pi Network : ⚠️ clé manquante"
    fi
else
    echo "   ⚠️ Fichier .env absent (dans ~/ia_web/)"
fi

# ---------- 5. Connectivité BSC ----------
echo ""
echo "⛓️ 5. BINANCE SMART CHAIN"
if python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); exit(0 if w3.is_connected() else 1)" 2>/dev/null; then
    BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(bal)" 2>/dev/null)
    echo "   ✅ Connecté – Solde: $BAL BNB"
else
    echo "   ❌ Déconnecté"
fi

# ---------- 6. Auto-dépannage des sessions tmux ----------
echo ""
echo "🛠️ 6. AUTO-DÉPANNAGE"
# Vérifier et redémarrer les sessions manquantes
for sess in ia_net pi_agents booster; do
    if ! tmux has-session -t $sess 2>/dev/null; then
        echo "   🔁 Session $sess absente → redémarrage"
        case $sess in
            ia_net) tmux new-session -d -s ia_net "python ia_net_pro.py" ;;
            pi_agents) tmux new-session -d -s pi_agents "python ia_pi_agents.py" ;;
            booster) tmux new-session -d -s booster "python ia_booster_pro.py" ;;
        esac
        echo "      ✅ $sess relancée"
    else
        echo "   ✅ Session $sess active"
    fi
done

# Redémarrer le backend Pi si nécessaire
if ! pgrep -f "pi_backend.py" > /dev/null; then
    echo "   🔁 Backend Pi arrêté → redémarrage"
    cd ~/ia_web && nohup python pi_backend.py > pi_backend.log 2>&1 &
    cd ~
    echo "      ✅ Backend Pi relancé"
else
    echo "   ✅ Backend Pi actif"
fi

# ---------- 7. Résumé final ----------
echo ""
echo "✅ DIAGNOSTIC TERMINÉ"
echo "   Pour voir les logs : tmux attach -t ia_net (ou pi_agents, booster)"
echo "   Pour surveiller : ./watch_general.sh"
