#!/bin/bash
# ============================================================
# MOTEUR ALL-IN-ONE avec PARTAGE DE DONNÉES entre bots
# ============================================================
SLEEP=30
CENTRAL_STATE="$HOME/ia_engine_state.json"
SHARED_STATE="$HOME/ia_shared_state.json"
LOG_FILE="$HOME/ia_engine.log"
TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.env 2>/dev/null | cut -d '=' -f2)
CHAT_ID=$(grep TELEGRAM_CHAT_ID ~/.env 2>/dev/null | cut -d '=' -f2)

declare -A SERVICES=(
    ["ia_net"]="ia_net_pro.py|$HOME"
    ["booster"]="ia_booster_pro.py|$HOME"
    ["booster_pro"]="ia_booster_pro_250.py|$HOME"
    ["hub"]="ia_hub_advanced.py|$HOME"
    ["hub_client"]="hub_client_advanced.py|$HOME"
    ["opp_auto"]="ia_opp_autonomous.py|$HOME"
    ["ia_reelle"]="main.py|$HOME/ia_mainnet_reelle"
)

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

send_telegram() {
    local msg="$1"
    [ -n "$TOKEN" ] && [ -n "$CHAT_ID" ] && curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" -d chat_id="$CHAT_ID" -d text="$msg" >/dev/null 2>&1
}

service_running() { tmux ls 2>/dev/null | grep -q "^$1:"; }

restart_service() {
    local name=$1
    local script_dir=${SERVICES[$name]#*|}
    local script=${SERVICES[$name]%|*}
    log "🔄 Redémarrage de $name"
    send_telegram "⚠️ Service $name redémarré à $(date)"
    tmux kill-session -t "$name" 2>/dev/null
    cd "$script_dir"
    tmux new-session -d -s "$name" "python $script"
    cd - >/dev/null
    sleep 2
    log "✅ $name redémarré"
}

auto_repair() {
    for name in "${!SERVICES[@]}"; do
        if ! service_running "$name"; then
            log "⚠️ $name arrêté → redémarrage"
            restart_service "$name"
        fi
    done
}

# Synchronisation des métriques et mise à jour du SHARED_STATE
sync_metrics() {
    ts=$(date +%s)
    echo "{}" > "$CENTRAL_STATE"
    
    # Mettre à jour le fichier partagé avec les dernières données
    if [ -f "$SHARED_STATE" ]; then
        cp "$SHARED_STATE" "$SHARED_STATE.bak"
    else
        echo '{"last_update":0}' > "$SHARED_STATE"
    fi
    
    # ia_net
    if [ -f "$HOME/ia_mem_pro.json" ]; then
        cycle=$(python3 -c "import json; d=json.load(open('$HOME/ia_mem_pro.json')); print(d.get('stats',{}).get('cycle',0))")
        actions=$(python3 -c "import json; d=json.load(open('$HOME/ia_mem_pro.json')); print(d.get('stats',{}).get('actions',0))")
        balance=$(python3 -c "import json; d=json.load(open('$HOME/ia_mem_pro.json')); print(d.get('last_balance',0))")
        echo "{\"ia_net\":{\"cycle\":$cycle,\"actions\":$actions,\"balance_bnb\":$balance,\"ts\":$ts}}" > "$CENTRAL_STATE"
        # Mettre à jour shared_state
        python3 << PY
import json
with open('$SHARED_STATE', 'r') as f:
    data = json.load(f)
data['last_update'] = $ts
data['ia_net'] = {'cycle': $cycle, 'actions': $actions, 'balance_bnb': $balance, 'ts': $ts}
with open('$SHARED_STATE', 'w') as f:
    json.dump(data, f, indent=2)
PY
    fi
    
    # ia_reelle
    if [ -f "$HOME/ia_mainnet_reelle/state.json" ]; then
        cycle2=$(python3 -c "import json; d=json.load(open('$HOME/ia_mainnet_reelle/state.json')); print(d.get('cycle',0))")
        usd=$(python3 -c "import json; d=json.load(open('$HOME/ia_mainnet_reelle/state.json')); print(d.get('total_earnings_usd',0))")
        echo "$(cat $CENTRAL_STATE | jq --argjson c $cycle2 --argjson u $usd --argjson t $ts '. + {ia_reelle: {cycle: $c, usd: $u, ts: $t}}')" > "$CENTRAL_STATE"
        python3 << PY
import json
with open('$SHARED_STATE', 'r') as f:
    data = json.load(f)
data['ia_reelle'] = {'cycle': $cycle2, 'usd_earned': $usd, 'ts': $ts}
with open('$SHARED_STATE', 'w') as f:
    json.dump(data, f, indent=2)
PY
    fi
    
    # opp_auto
    if [ -f "$HOME/ia_opp_mem.json" ]; then
        opp_cycle=$(python3 -c "import json; d=json.load(open('$HOME/ia_opp_mem.json')); print(d.get('stats',{}).get('cycle',0))")
        opp_list=$(python3 -c "import json; d=json.load(open('$HOME/ia_opp_mem.json')); print(json.dumps(d.get('opportunities',[])[-5:]))")
        echo "$(cat $CENTRAL_STATE | jq --argjson oc $opp_cycle --argjson t $ts '. + {opp_auto: {cycle: $oc, ts: $t}}')" > "$CENTRAL_STATE"
        python3 << PY
import json
with open('$SHARED_STATE', 'r') as f:
    data = json.load(f)
data['opp_auto'] = {'cycle': $opp_cycle, 'opportunities': $opp_list, 'ts': $ts}
with open('$SHARED_STATE', 'w') as f:
    json.dump(data, f, indent=2)
PY
    fi
    
    # Ajouter une commande test (ex: le moteur peut écrire une commande pour les bots)
    # Les bots peuvent lire SHARED_STATE et exécuter des actions.
}

dashboard() {
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "  🧠 MOTEUR ALL-IN-ONE | Partage de données activé"
    echo "════════════════════════════════════════════════════════════════"
    echo "⏱️  Dernier cycle : $(date)"
    echo ""
    for name in "${!SERVICES[@]}"; do
        if service_running "$name"; then
            echo -e "   ✅ $name : \033[32mactif\033[0m"
        else
            echo -e "   ❌ $name : \033[31marrêté\033[0m"
        fi
    done
    echo ""
    if [ -f "$SHARED_STATE" ]; then
        echo "📡 ÉTAT PARTAGÉ (dernières valeurs) :"
        cat "$SHARED_STATE" | jq '{ia_net: .ia_net, ia_reelle: .ia_reelle, opp_auto: .opp_auto, last_update: .last_update}' 2>/dev/null | sed 's/^/   /'
    else
        echo "   Aucun état partagé"
    fi
    echo ""
    echo "🔄 Rafraîchi toutes les $SLEEP secondes"
}

main_loop() {
    log "🚀 Moteur All-in-One avec partage de données démarré"
    send_telegram "✅ Partage de données activé sur $(hostname)"
    while true; do
        auto_repair
        sync_metrics
        dashboard
        sleep "$SLEEP"
    done
}
main_loop

# Ajout au moteur : possibilité d'écrire des commandes croisées
send_command() {
    local target=$1
    local cmd=$2
    python3 -c "
import json, time
with open('$SHARED_STATE', 'r') as f:
    data = json.load(f)
commands = data.get('commands', [])
commands.append({'id': int(time.time()), 'target': '$target', 'cmd': '$cmd', 'issued_by': 'engine'})
data['commands'] = commands[-50:]  # garder les 50 dernières
with open('$SHARED_STATE', 'w') as f:
    json.dump(data, f, indent=2)
"
    log "📢 Commande '$cmd' ajoutée pour $target"
}
