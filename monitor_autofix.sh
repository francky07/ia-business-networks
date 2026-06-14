#!/data/data/com.termux/files/usr/bin/bash
# IA NetSolutions PRO - Surveillance temps réel + auto-dépannage
# Lancez ce script dans un terminal dédié. Quitter avec Ctrl+C.

while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║     IA NetSolutions PRO - Surveillance & Auto-dépannage (live)    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    date
    echo ""

    # --- 1. Vérification des sessions tmux et auto-redémarrage ---
    echo "🖥️ SESSIONS TMUX"
    for sess in ia_net pi_agents booster; do
        if tmux has-session -t $sess 2>/dev/null; then
            echo "   ✅ $sess active"
        else
            echo "   ⚠️ $sess absente → redémarrage"
            case $sess in
                ia_net)   tmux new-session -d -s ia_net "python ia_net_pro.py" ;;
                pi_agents) tmux new-session -d -s pi_agents "python ia_pi_agents.py" ;;
                booster)  tmux new-session -d -s booster "python ia_booster_pro.py" ;;
            esac
            sleep 1
            echo "      ✅ $sess relancée"
        fi
    done
    # Backend Pi
    if pgrep -f "pi_backend.py" > /dev/null; then
        echo "   ✅ Backend Pi actif"
    else
        echo "   ⚠️ Backend Pi arrêté → redémarrage"
        cd ~/ia_web && nohup python pi_backend.py > pi_backend.log 2>&1 &
        cd ~
        echo "      ✅ Backend Pi relancé"
    fi
    echo ""

    # --- 2. Connectivité BSC ---
    echo "⛓️ BINANCE SMART CHAIN"
    if python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); exit(0 if w3.is_connected() else 1)" 2>/dev/null; then
        BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(f'{bal:.8f}')" 2>/dev/null)
        echo "   ✅ Connecté – Solde: $BAL BNB"
    else
        echo "   ❌ Déconnecté (vérifiez réseau)"
    fi
    echo ""

    # --- 3. Services externes (GitHub, Telegram, OpenAI) ---
    echo "🛡️ SERVICES"
    TOKEN=$(grep '^GITHUB_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$TOKEN" ]; then
        curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null && echo "   🐙 GitHub : ✅" || echo "   🐙 GitHub : ❌"
    else
        echo "   🐙 GitHub : ⚠️ token manquant"
    fi
    BOT=$(grep '^TELEGRAM_BOT_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$BOT" ]; then
        curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true' && echo "   📡 Telegram : ✅" || echo "   📡 Telegram : ❌"
    else
        echo "   📡 Telegram : ⚠️ non configuré"
    fi
    KEY=$(grep '^OPENAI_API_KEY' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -n "$KEY" ]; then
        curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null && echo "   🤖 OpenAI : ✅" || echo "   🤖 OpenAI : ❌"
    else
        echo "   🤖 OpenAI : ⚠️ non configuré"
    fi
    echo ""

    # --- 4. Infura et Pi (via .env) ---
    echo "🔌 INFURA"
    INFURA_KEY=$(grep '^INFURA_KEY=' ~/ia_web/.env 2>/dev/null | cut -d'=' -f2)
    if [ -n "$INFURA_KEY" ]; then
        python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/$INFURA_KEY')); exit(0 if w3.is_connected() else 1)" 2>/dev/null && echo "   ✅ Connecté" || echo "   ❌ Déconnecté"
    else
        echo "   ⚠️ Clé manquante"
    fi
    echo "🥧 Pi NETWORK"
    PI_KEY=$(grep '^PI_API_KEY=' ~/ia_web/.env 2>/dev/null | cut -d'=' -f2)
    if [ -n "$PI_KEY" ]; then
        curl -s -H "Authorization: Key $PI_KEY" https://api.minepi.com/v2/me > /dev/null && echo "   ✅ API OK" || echo "   ❌ API KO"
    else
        echo "   ⚠️ Clé manquante"
    fi
    echo ""

    # --- 5. Dernières lignes des logs (aperçu) ---
    echo "📋 APERÇU DES LOGS (5 dernières lignes)"
    echo "   BOT PRINCIPAL :"
    tmux capture-pane -pt ia_net -S -5 2>/dev/null | tail -5 | sed 's/^/      /' || echo "      Session ia_net introuvable"
    echo "   BOOSTER :"
    tmux capture-pane -pt booster -S -5 2>/dev/null | tail -5 | sed 's/^/      /' || echo "      Session booster introuvable"
    echo "   AGENTS Pi :"
    tmux capture-pane -pt pi_agents -S -5 2>/dev/null | tail -5 | sed 's/^/      /' || echo "      Session pi_agents introuvable"
    echo ""

    # --- 6. Correction du fichier mémoire si corrompu ---
    if [ -f ia_mem_pro.json ]; then
        if ! python -c "import json; json.load(open('ia_mem_pro.json'))" 2>/dev/null; then
            echo "⚠️ Fichier mémoire corrompu → recréation"
            rm -f ia_mem_pro.json
            echo '{"stats":{"cycle":0,"actions":0},"errors":[],"last_balance":0.0}' > ia_mem_pro.json
            echo "   ✅ Fichier recréé"
        fi
    fi
    echo ""

    echo "🔄 Rafraîchi toutes les 15 secondes (Ctrl+C pour quitter)"
    sleep 15
done
