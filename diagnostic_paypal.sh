#!/bin/bash
echo "════════════════════════════════════════════════════════════════"
echo "  💳 DIAGNOSTIC PAYPAL (API + IMAP)"
echo "════════════════════════════════════════════════════════════════"
echo "Date : $(date)"
echo ""
echo "🔑 Clés API PayPal :"
source ~/.env_ia_business
if [ -n "$PAYPAL_API_CLIENT_ID" ]; then
    echo "   Client ID : ${PAYPAL_API_CLIENT_ID:0:20}..."
else
    echo "   ❌ Client ID manquant"
fi
if [ -n "$PAYPAL_API_CLIENT_SECRET" ]; then
    echo "   Client Secret : ${PAYPAL_API_CLIENT_SECRET:0:20}..."
else
    echo "   ❌ Client Secret manquant"
fi
echo "   Mode : $PAYPAL_API_MODE"
echo ""
echo "🌐 Test de l'API PayPal (obtention du token) :"
AUTH=$(printf "%s:%s" "$PAYPAL_API_CLIENT_ID" "$PAYPAL_API_CLIENT_SECRET" | base64 | tr -d '\n')
URL="https://api-m.sandbox.paypal.com/v1/oauth2/token"
[ "$PAYPAL_API_MODE" = "live" ] && URL="https://api-m.paypal.com/v1/oauth2/token"
RESP=$(curl -s -X POST "$URL" -H "Authorization: Basic $AUTH" -H "Content-Type: application/x-www-form-urlencoded" -d "grant_type=client_credentials")
if echo "$RESP" | grep -q '"access_token"'; then
    echo "   ✅ Token obtenu"
else
    echo "   ❌ Échec : $RESP"
fi
echo ""
echo "📧 Test IMAP Gmail :"
if [ -n "$PAYPAL_IMAP_PASSWORD" ]; then
    echo "   Email : $PAYPAL_EMAIL"
    echo "   Mot de passe d'application : configuré"
    # Test de connexion IMAP (simple)
    python3 -c "
import imaplib
try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('$PAYPAL_EMAIL', '$PAYPAL_IMAP_PASSWORD')
    print('   ✅ Connexion IMAP réussie')
    mail.close()
    mail.logout()
except Exception as e:
    print(f'   ❌ Échec IMAP: {e}')
"
else
    echo "   ⚠️ PAYPAL_IMAP_PASSWORD non défini"
fi
echo ""
echo "════════════════════════════════════════════════════════════════"
