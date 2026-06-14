#!/bin/bash
while true; do
    # 1. Télécharger la page d'inscription de Blockchain.com
    curl -s "https://www.blockchain.com/register/" -o /tmp/blockchain.html
    # 2. Extraire l'URL de l'image captcha (à adapter selon la structure HTML)
    CAPTCHA_URL=$(grep -oP 'src="\K[^"]+' /tmp/blockchain.html | grep -i captcha | head -1)
    if [ -n "$CAPTCHA_URL" ]; then
        # Construire l'URL absolue si nécessaire
        if [[ "$CAPTCHA_URL" != http* ]]; then
            CAPTCHA_URL="https://www.blockchain.com$CAPTCHA_URL"
        fi
        curl -s -o ~/oeil_de_dieu/captcha.png "$CAPTCHA_URL"
        echo "Captcha téléchargé à $(date)"
    else
        echo "Aucun captcha trouvé sur la page – la structure a peut-être changé"
    fi
    sleep 60
done
