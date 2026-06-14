#!/bin/bash
tmux kill-server 2>/dev/null
sleep 2
cd ~
[ -f ~/agence_kays/agence.py ] && tmux new-session -d -s agence_kays "python ~/agence_kays/agence.py"
[ -f ~/departement_ventes/sell_emails_paypal.py ] && tmux new-session -d -s ventes "python ~/departement_ventes/sell_emails_paypal.py"
[ -f ~/ia_nexus/core/nexus_brain.py ] && tmux new-session -d -s nexus_brain "python ~/ia_nexus/core/nexus_brain.py"
[ -f ~/ia_booster_agence.py ] && tmux new-session -d -s booster_agence "python ~/ia_booster_agence.py"
[ -f ~/dashboard_nexus.sh ] && tmux new-session -d -s nexus_dashboard "bash ~/dashboard_nexus.sh"
echo "✅ Redémarrage effectué"
