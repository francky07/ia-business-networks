import smtplib, ssl, os

# Lire la config
cfg = {}
with open(os.path.expanduser("~/.secrets/gmail.conf")) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            cfg[k] = v.strip()

try:
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls(context=context)
        s.login(cfg['GMAIL_EMAIL'], cfg['GMAIL_APP_PASSWORD'])
        print("✅ Authentification Gmail réussie !")
except Exception as e:
    print(f"❌ Échec : {e}")
