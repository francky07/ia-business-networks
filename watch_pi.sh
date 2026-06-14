#!/data/data/com.termux/files/usr/bin/bash
# Surveillance des agents Pi Network (IA NetSolutions PRO)
clear
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           IA NetSolutions PRO - Agents Pi Network                  ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
date
echo ""

echo "🔌 ÉTAT DE L'API Pi"
PI_API_KEY=$(grep '^PI_API_KEY=' ~/ia_web/.env 2>/dev/null | cut -d'=' -f2)
if [ -n "$PI_API_KEY" ]; then
    if curl -s -H "Authorization: Key $PI_API_KEY" https://api.minepi.com/v2/me > /dev/null 2>&1; then
        echo "   ✅ Clé API valide"
    else
        echo "   ❌ Clé API invalide ou erreur réseau"
    fi
else
    echo "   ⚠️ Clé API manquante (configurez ~/ia_web/.env)"
fi
echo ""

echo "💰 PAIEMENTS Pi RÉCENTS (depuis ia_mem_pro.json)"
python3 -c "
import json, os
mem_file = 'ia_mem_pro.json'
if os.path.exists(mem_file):
    with open(mem_file) as f:
        data = json.load(f)
    payments = data.get('pi_pending_payments', [])[-5:]
    if payments:
        for p in payments:
            print(f\"   ID: {p.get('identifier', 'N/A')} | Montant: {p.get('amount', '?')} Pi | Statut: {p.get('status', '?')}\")
    else:
        print('   Aucun paiement récent')
else:
    print('   Fichier mémoire introuvable')
" 2>/dev/null
echo ""

echo "👥 UTILISATEURS Pi CONNECTÉS"
python3 -c "
import json, os
mem_file = 'ia_mem_pro.json'
if os.path.exists(mem_file):
    with open(mem_file) as f:
        data = json.load(f)
    users = data.get('pi_active_users', [])
    if users:
        for u in users[-5:]:
            print(f\"   UID: {u.get('uid', '?')} | Nom: {u.get('username', '?')}\")
    else:
        print('   Aucun utilisateur actif')
else:
    print('   Fichier mémoire introuvable')
" 2>/dev/null
echo ""

echo "🖥️ AGENTS Pi NETWORK ACTIFS"
NB_AGENTS=$(ps aux | grep -c "PiEco" 2>/dev/null || echo "0")
if [ "$NB_AGENTS" -gt 0 ]; then
    echo "   ✅ $NB_AGENTS threads Pi actifs (sur 250)"
else
    echo "   ⚠️ Aucun thread Pi détecté (vérifiez ia_net_pro.py)"
fi
echo ""

echo "🔄 Rafraîchi toutes les 10 secondes (Ctrl+C pour quitter)"
