#!/data/data/com.termux/files/usr/bin/bash
# Script complet pour IA NetSolutions
echo "========================================="
echo "  IA NetSolutions - Déploiement complet"
echo "========================================="

# 1. Vérifier les dépendances
echo "📦 Vérification des dépendances..."
pkg update -y && pkg install -y python tmux
pip install --upgrade pip
pip install web3 requests ecdsa flask flask_cors telegram-python-bot

# 2. S'assurer que le script principal est présent et corrigé
if [ ! -f ia_net.py ]; then
    echo "❌ ia_net.py manquant, veuillez exécuter d'abord l'installation"
    exit 1
fi

# 3. Vérifier que le token GitHub est présent (sinon demander)
if ! grep -q '^GITHUB_TOKEN = "' ia_net.py || grep -q '^GITHUB_TOKEN = ""' ia_net.py; then
    echo "🔑 Token GitHub manquant ou vide."
    read -s -p "Collez votre token GitHub (créé avec droits 'repo') : " gh_token
    sed -i "s/^GITHUB_TOKEN = \".*\"/GITHUB_TOKEN = \"$gh_token\"/" ia_net.py
    echo "✅ Token GitHub ajouté"
fi

# 4. Nettoyer les anciennes sessions tmux
tmux kill-session -t ia_net 2>/dev/null

# 5. Lancer le bot dans tmux
echo "🚀 Démarrage du bot..."
tmux new-session -d -s ia_net "python ia_net.py"
sleep 3

# 6. Vérifier que le bot tourne
if pgrep -f "ia_net.py" > /dev/null; then
    echo "✅ Bot lancé avec succès (PID: $(pgrep -f ia_net.py | tr '\n' ' '))"
else
    echo "❌ Échec du démarrage, vérifiez les logs : python ia_net.py"
    exit 1
fi

# 7. Afficher les commandes utiles
echo ""
echo "📌 Commandes :"
echo "   Voir les logs   : tmux attach -t ia_net"
echo "   Quitter tmux    : Ctrl+B puis D"
echo "   Arrêter le bot  : tmux kill-session -t ia_net"
echo "   Redémarrer      : ./complete_bot.sh"
echo "========================================="
