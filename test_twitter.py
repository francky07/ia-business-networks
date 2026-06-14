import tweepy
import os

api_key = os.environ.get("TWITTER_API_KEY")
api_secret = os.environ.get("TWITTER_API_SECRET")
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

if not all([api_key, api_secret, access_token, access_secret]):
    print("❌ Clés manquantes")
    exit(1)

try:
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    user = api.verify_credentials()
    print(f"✅ Authentification réussie. Compte : @{user.screen_name}")
    print("Tentative d'envoi d'un tweet test...")
    tweet = api.update_status("Test de diagnostic (automatique) - sera supprimé")
    print(f"   ✅ Tweet posté (ID: {tweet.id})")
    api.destroy_status(tweet.id)
    print("   ✅ Tweet supprimé. L'écriture fonctionne correctement.")
    print("\n💡 Votre bot pourra poster des tweets et gagner 0.02 USD par cycle.")
except Exception as e:
    print(f"❌ Erreur Twitter : {e}")
    if "403" in str(e):
        print("   → Permission refusée (403). Vérifiez les droits 'Read and write' de votre application.")
    elif "401" in str(e):
        print("   → Clés invalides (401). Régénérez les tokens.")
