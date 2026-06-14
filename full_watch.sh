# #!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# IA NetSolutions - Full Watch (tous les bots)
# Lancez ce script dans un terminal séparé.
# Rafraîchi toutes les 5 secondes. Quitter avec Ctrl+C.
# ============================================================

while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                 IA NetSolutions - Full Watch (tous les bots)       ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    date
    echo ""

    echo "📌 BOT PRINCIPAL (ia_net) :"
    tmux capture-pane -pt ia_net -S -8 2>/dev/null | tail -8 || echo "   Session absente"
    echo ""

    echo "📌 BOOSTER STANDARD (booster) :"
    tmux capture-pane -pt booster -S -8 2>/dev/null | tail -8 || echo "   Session absente"
    echo ""

    echo "📌 BOOSTER PRO (booster_pro) :"
    tmux capture-pane -pt booster_pro -S -8 2>/dev/null | tail -8 || echo "   Session absente"
    echo ""

    echo ""

    echo "📌 HUB (hub) :"
    tmux capture-pane -pt hub -S -8 2>/dev/null | tail -8 || echo "   Session absente"
    echo ""

    echo "📌 CLIENT HUB (hub_client) :"
    tmux capture-pane -pt hub_client -S -8 2>/dev/null | tail -8 || echo "   Session absente"
    echo ""

    echo "📌 DASHBOARD (dashboard) :"
    tmux capture-pane -pt dashboard -S -8 2>/dev/null | tail -8 || echo "   Session absente"
    echo ""

    echo "🔄 Rafraîchi toutes les 5 secondes (Ctrl+C pour quitter)"
    sleep 5
done
