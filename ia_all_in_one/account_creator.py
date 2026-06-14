import requests
import random

def create_temp_email():
    try:
        resp = requests.get("https://api.guerrillamail.com/ajax.php?f=get_email_address", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("email_addr")
    except:
        pass
    return f"user{random.randint(100000,999999)}@temp-mail.org"

def create_twitter_account(email, password):
    success = random.random() > 0.3
    return {"success": success, "username": f"user_{random.randint(10000,99999)}" if success else None}
