#!/bin/bash
cd ~
for s in ia_net booster booster_pro hub hub_client opp_auto finance finance_booster ia_reelle; do
    tmux kill-session -t $s 2>/dev/null
done
for script in ia_net_pro.py ia_booster_pro.py ia_booster_pro_250.py ia_hub_advanced.py hub_client_advanced.py ia_opp_autonomous.py ia_finance_500.py ia_finance_booster_500.py; do
    if [ -f "$script" ]; then
        tmux new-session -d -s "${script%.py}" "python $script"
        echo "✅ ${script%.py}"
    fi
done
if [ -d ~/ia_mainnet_reelle ]; then
    cd ~/ia_mainnet_reelle
    tmux new-session -d -s ia_reelle "python main.py 2>&1 | tee business.log"
    echo "✅ ia_reelle (mode réel)"
fi
echo "✅ Tout est relancé"
