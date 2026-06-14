#!/bin/bash
while true; do
    # Télécharge la page de démonstration de Google reCAPTCHA
    curl -s "https://www.google.com/recaptcha/api2/demo" -o /tmp/demo.html
    # Extrait l'URL de l'image captcha (elle change à chaque visite)
    CAPTCHA_URL=$(grep -oP 'src="\K[^"]+' /tmp/demo.html | grep 'recaptcha' | head -1)
    if [ -n "$CAPTCHA_URL" ]; then
        curl -s -o ~/oeil_de_dieu/captcha.png "https://www.google.com$CAPTCHA_URL"
        echo "Captcha téléchargé à $(date)"
    else
        echo "Aucun captcha trouvé, réessai..."
    fi
    sleep 60
done
