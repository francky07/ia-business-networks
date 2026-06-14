#!/bin/bash
while true; do
    for s in agence_kays ventes ia_net booster hub opp_auto nexus_brain mega_scraper; do
        if ! tmux has-session -t $s 2>/dev/null; then
            echo "Relance de $s"
            case $s in
                agence_kays) tmux new-session -d -s agence_kays "python ~/agence_kays/agence.py" ;;
                ventes) tmux new-session -d -s ventes "cd ~/departement_ventes && python ventes.py" ;;
                ia_net) tmux new-session -d -s ia_net "python ~/ia_net_pro.py" ;;
                nexus_brain) tmux new-session -d -s nexus_brain "cd ~/ia_nexus && python core/nexus_brain.py" ;;
                mega_scraper) tmux new-session -d -s mega_scraper "python ~/ia_nexus/scrapers/mega_scraper.py" ;;
            esac
        fi
    done
    sleep 30
done
