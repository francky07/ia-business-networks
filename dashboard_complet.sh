#!/bin/bash
# ============================================================
# Tableau de bord intégral - IA Business (tous modules)
# ============================================================

export LANG=C
export LC_ALL=C

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Chemins
MAINNET_DIR="$HOME/ia_mainnet_reelle"
FINANCE_MEM="$HOME/ia_finance_mem.json"
MAIN_MEM="$HOME/ia_mem_pro.json"
MAINNET_WALLET="$MAINNET_DIR/wallet.json"
MAINNET_STATE="$MAINNET_DIR/state.json"
HUB_STATE="$HOME/hub_state.json"  # optionnel

# Fonction pour lire une valeur JSON avec Python
json_val() {
    python3 -c "import json,sys; data=json.load(open('$1')); print(data.get('$2', 0))" 2>/dev/null || echo "0"
}

# Collecte des données
collect_data() {
    # --- Nouveau modèle réel ---
    if [ -f "$MAINNET_WALLET" ]; then
        BNB_REEL=$(json_val "$MAINNET_WALLET" "bnb_balance")
        USD_REEL=$(json_val "$MAINNET_WALLET" "total_earnings_usd")
    else
        BNB_REEL=0
        USD_REEL=0
    fi
    if [ -f "$MAINNET_STATE" ]; then
        CYCLE_REEL=$(json_val "$MAINNET_STATE" "cycle")
    else
        CYCLE_REEL=0
    fi

    # --- Module Finance ---
    if [ -f "$FINANCE_MEM" ]; then
        REVENUE_FIN=$(python3 -c "import json; d=json.load(open('$FINANCE_MEM')); print(d.get('stats',{}).get('revenue',0))" 2>/dev/null || echo "0")
        CYCLE_FIN=$(python3 -c "import json; d=json.load(open('$FINANCE_MEM')); print(d.get('stats',{}).get('cycle',0))" 2>/dev/null || echo "0")
    else
        REVENUE_FIN=0
        CYCLE_FIN=0
    fi

    # --- Bot principal ia_net ---
    if [ -f "$MAIN_MEM" ]; then
        CYCLE_MAIN=$(python3 -c "import json; d=json.load(open('$MAIN_MEM')); print(d.get('stats',{}).get('cycle',0))" 2>/dev/null || echo "0")
        ACTIONS_MAIN=$(python3 -c "import json; d=json.load(open('$MAIN_MEM')); print(d.get('stats',{}).get('actions',0))" 2>/dev/null || echo "0")
        ERRORS_MAIN=$(python3 -c "import json; d=json.load(open('$MAIN_MEM')); print(len(d.get('errors',[])))" 2>/dev/null || echo "0")
    else
        CYCLE_MAIN=0
        ACTIONS_MAIN=0
        ERRORS_MAIN=0
    fi

    # --- Sessions tmux ---
    TMUX_SESSIONS=$(tmux ls 2>/dev/null | awk '{print $1}' | sed 's/://' | tr '\n' ' ')
}

# Affichage
show_dashboard() {
    clear
    echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}   🌐 IA BUSINESS - TABLEAU DE BORD INTÉGRAL (tous modules)${NC}"
    echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}Date :${NC} $(date)"
    echo ""

    # --- Nouveau modèle réel ---
    echo -e "${BOLD}${GREEN}📌 NOUVEAU MODÈLE RÉEL (ia_mainnet_reelle)${NC}"
    echo -e "   Cycle       : ${YELLOW}$CYCLE_REEL${NC}"
    echo -e "   Gains USD   : ${YELLOW}$(printf "%.2f" $USD_REEL)${NC}"
    echo -e "   Solde BNB   : ${YELLOW}$(printf "%.6f" $BNB_REEL)${NC}"
    echo ""

    # --- Module Finance ---
    echo -e "${BOLD}${GREEN}📌 FINANCE (500 agents)${NC}"
    echo -e "   Cycle       : ${YELLOW}$CYCLE_FIN${NC}"
    echo -e "   Revenu USD  : ${YELLOW}$(printf "%.2f" $REVENUE_FIN)${NC}"
    echo ""

    # --- Bot principal ia_net ---
    echo -e "${BOLD}${GREEN}📌 BOT PRINCIPAL (ia_net)${NC}"
    echo -e "   Cycle       : ${YELLOW}$CYCLE_MAIN${NC}"
    echo -e "   Actions     : ${YELLOW}$ACTIONS_MAIN${NC}"
    echo -e "   Erreurs     : ${YELLOW}$ERRORS_MAIN${NC}"
    echo ""

    # --- Autres composants (boosters, hub, annexe) ---
    echo -e "${BOLD}${GREEN}📌 AUTRES COMPOSANTS${NC}"
    if tmux ls 2>/dev/null | grep -q booster; then echo -e "   ✅ Boosters (standard/pro) : actifs"; else echo -e "   ❌ Boosters : inactifs"; fi
    if tmux ls 2>/dev/null | grep -q hub; then echo -e "   ✅ Hub central : actif"; else echo -e "   ❌ Hub : inactif"; fi
    if tmux ls 2>/dev/null | grep -q opp_auto; then echo -e "   ✅ Annexe (veille) : active"; else echo -e "   ❌ Annexe : inactive"; fi
    echo ""

    # --- Sessions tmux actives ---
    echo -e "${BOLD}${GREEN}🖥️ SESSIONS TMUX ACTIVES${NC}"
    if [ -n "$TMUX_SESSIONS" ]; then
        for s in $TMUX_SESSIONS; do
            echo -e "   ✅ ${CYAN}$s${NC}"
        done
    else
        echo -e "   ${RED}Aucune session tmux${NC}"
    fi
    echo ""

    # --- Dernières erreurs ---
    echo -e "${BOLD}${YELLOW}⚠️ DERNIÈRES ERREURS (extrait des logs)${NC}"
    # Logs du nouveau modèle
    if [ -f "$MAINNET_DIR/business.log" ]; then
        ERR=$(grep -i error "$MAINNET_DIR/business.log" 2>/dev/null | tail -1 | sed 's/^/   /')
        if [ -n "$ERR" ]; then echo -e "   $ERR"; else echo "   Aucune erreur récente (nouveau modèle)"; fi
    fi
    # Logs du bot principal
    if [ -f "$HOME/business.log" ]; then
        ERR2=$(grep -i error "$HOME/business.log" 2>/dev/null | tail -1 | sed 's/^/   /')
        if [ -n "$ERR2" ]; then echo -e "   $ERR2"; else echo "   Aucune erreur récente (ia_net)"; fi
    fi
    echo ""

    echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}Rafraîchi toutes les 10 secondes (Ctrl+C pour quitter)${NC}"
}

# Boucle principale
while true; do
    collect_data
    show_dashboard
    sleep 10
done
