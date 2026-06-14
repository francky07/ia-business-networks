#!/bin/bash
echo "════════════════════════════════════════════════════════════════"
echo "  🔍 DEEP DIAGNOSTIC – IA BUSINESS (tous services)"
echo "════════════════════════════════════════════════════════════════"
echo "Date : $(date)"
echo ""
echo "🖥️ SESSIONS TMUX ACTIVES :"
tmux ls 2>/dev/null | awk '{print "   ✅ " $1}' || echo "   ❌ Aucune session"
echo ""
echo "🐍 PROCESSUS PYTHON (bots) :"
ps aux | grep -E "ia_|main\.py|play_2captcha" | grep -v grep | awk '{print "   ✅ " $12 " (PID " $2 ")"}' || echo "   ❌ Aucun processus"
echo ""
echo "📌 MODULE RÉEL (ia_mainnet_reelle) :"
if [ -f ~/ia_mainnet_reelle/state.json ]; then
    cycle2=$(python3 -c "import json; d=json.load(open('~/ia_mainnet_reelle/state.json')); print(d.get('cycle',0))")
    usd=$(python3 -c "import json; d=json.load(open('~/ia_mainnet_reelle/state.json')); print(d.get('total_earnings_usd',0))")
    echo "   Cycle : $cycle2 | Gains USD bruts : $usd"
else
    echo "   ⚠️ state.json absent"
fi
if [ -f ~/ia_mainnet_reelle/wallet.json ]; then
    bnb=$(python3 -c "import json; d=json.load(open('~/ia_mainnet_reelle/wallet.json')); print(d.get('bnb_balance',0))")
    tot=$(python3 -c "import json; d=json.load(open('~/ia_mainnet_reelle/wallet.json')); print(d.get('total_earnings_usd',0))")
    echo "   BNB converti : $bnb | Total USD convertis : $tot"
fi
echo ""
echo "💰 SOLDE BNB RÉEL (wallet 0xba23A87e...) :"
python3 -c "from web3 import Web3; w3=Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org')); bal=w3.from_wei(w3.eth.get_balance('0xba23A87e6f67a1becC59AAEd4c2DDa8C216F9363'), 'ether'); print(f'   {bal:.8f} BNB')" 2>/dev/null || echo "   ❌ Erreur BSC"
echo ""
echo "⚠️ DERNIÈRES ERREURS (extrait des logs récents) :"
if [ -f ~/ia_mainnet_reelle/business.log ]; then
    tail -5 ~/ia_mainnet_reelle/business.log | grep -i error | tail -1 | sed 's/^/   /' || echo "   ✅ Aucune erreur récente"
else
    echo "   Pas de log"
fi
echo "════════════════════════════════════════════════════════════════"
echo "✅ Diagnostic terminé"
