import smtplib, ssl
from email.mime.text import MIMEText

SMTP_USER = "votre_utilisateur"
SMTP_PASSWORD = "votre_mot_de_passe"
dest = "test@exemple.com"

msg = MIMEText("test", 'plain')
msg['Subject'] = "Test"
msg['From'] = SMTP_USER
msg['To'] = dest

try:
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.ai-net.com", 587) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    print("Succès")
except Exception as e:
    print("Erreur:", e)
