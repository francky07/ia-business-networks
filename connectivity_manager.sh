# Collez le contenu ci-dessus, sauvegardez (Ctrl+O, Entrée, Ctrl+X)#!/data/data/com.termux/files/usr/bin/bash
# Gestionnaire de connectivité IA NetSolutions PRO
# Auteur : IA NetSolutions
# Usage : ./connectivity_manager.sh

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Gestionnaire de connectivité IA NetSolutions"
echo "=========================================="

# Fonction de test et correction
test_bsc() {
    echo -n "⛓️  BSC : "
    if python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); exit(0 if w3.is_connected() else 1)" 2>/dev/null; then
        BAL=$(python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(bal)" 2>/dev/null)
        echo -e "${GREEN}OK${NC} (solde: $BAL BNB)"
    else
        echo -e "${RED}KO${NC}"
        echo "   -> Vérifiez votre connexion internet ou changez d'endpoint RPC"
    fi
}

test_github() {
    echo -n "🐙 GitHub : "
    TOKEN=$(grep '^GITHUB_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -z "$TOKEN" ]; then
        echo -e "${YELLOW}⚠️  token manquant${NC}"
        echo "   -> Ajoutez GITHUB_TOKEN dans ia_net_pro.py"
        return
    fi
    if curl -s -H "Authorization: token $TOKEN" https://api.github.com/user > /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}KO${NC}"
        echo "   -> Token invalide ou expiré. Régénérez-le sur GitHub (droits 'repo')"
    fi
}

test_telegram() {
    echo -n "📡 Telegram : "
    BOT=$(grep '^TELEGRAM_BOT_TOKEN' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -z "$BOT" ]; then
        echo -e "${YELLOW}⚠️  non configuré${NC}"
        return
    fi
    if curl -s "https://api.telegram.org/bot${BOT}/getMe" | grep -q '"ok":true'; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}KO${NC}"
        echo "   -> Token invalide. Recréez un bot via @BotFather"
    fi
}

test_openai() {
    echo -n "🤖 OpenAI : "
    KEY=$(grep '^OPENAI_API_KEY' ia_net_pro.py 2>/dev/null | cut -d'"' -f2)
    if [ -z "$KEY" ]; then
        echo -e "${YELLOW}⚠️  non configuré${NC}"
        return
    fi
    if curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models > /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}KO${NC}"
        echo "   -> Clé invalide ou quota épuisé"
    fi
}

test_infura() {
    echo -n "🔌 Infura : "
    INFURA_KEY=$(grep '^INFURA_KEY=' ~/ia_web/.env 2>/dev/null | cut -d'=' -f2)
    if [ -z "$INFURA_KEY" ]; then
        echo -e "${YELLOW}⚠️  clé manquante${NC}"
        return
    fi
    if python -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/$INFURA_KEY')); exit(0 if w3.is_connected() else 1)" 2>/dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}KO${NC}"
        echo "   -> Clé invalide ou réseau. Vérifiez votre clé Infura"
    fi
}

test_pi() {
    echo -n "🥧 Pi API : "
    PI_KEY=$(grep '^PI_API_KEY=' ~/ia_web/.env 2>/dev/null | cut -d'=' -f2)
    if [ -z "$PI_KEY" ]; then
        echo -e "${YELLOW}⚠️  clé manquante${NC}"
        return
    fi
    # Utilisation d'un endpoint qui accepte la clé API (ex: /v2/apps)
    if curl -s -H "Authorization: Key $PI_KEY" https://api.minepi.com/v2/apps > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}KO${NC}"
        echo "   -> Clé invalide ou API injoignable"
    fi
}

# --- Actions correctives ---
repair_sessions() {
    echo ""
    echo "🔧 Vérification des sessions tmux..."
    for sess in ia_net pi_agents booster stability; do
        if ! tmux has-session -t $sess 2>/dev/null; then
            echo "   🔁 Session $sess absente → redémarrage"
            case $sess in
                ia_net)   tmux new-session -d -s ia_net "python ia_net_pro.py" ;;
                pi_agents) tmux new-session -d -s pi_agents "python ia_pi_agents.py" ;;
                booster)  tmux new-session -d -s booster "python ia_booster_pro.py" ;;
                stability) tmux new-session -d -s stability "python ia_stability_agency.py" ;;
            esac
            echo "      ✅ $sess relancée"
        else
            echo "   ✅ $sess active"
        fi
    done
}

repair_backend_pi() {
    if ! pgrep -f "pi_backend.py" > /dev/null; then
        echo "   🔁 Backend Pi arrêté → redémarrage"
        cd ~/ia_web && nohup python pi_backend.py > pi_backend.log 2>&1 &
        cd ~
        echo "      ✅ Backend Pi relancé"
    else
        echo "   ✅ Backend Pi actif"
    fi
}

# --- Exécution principale ---
echo ""
echo "=== Diagnostic des services ==="
test_bsc
test_github
test_telegram
test_openai
test_infura
test_pi

echo ""
echo "=== Actions correctives ==="
repair_sessions
repair_backend_pi

echo ""
echo "✅ Gestionnaire de connectivité terminé."
echo "   Si des problèmes persistent, exécutez à nouveau ou vérifiez les clés API."
