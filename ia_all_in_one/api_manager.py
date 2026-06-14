import json
import random
import string
import requests
from config import API_KEYS_DB, GITHUB_TOKEN

def load_api_keys():
    try:
        with open(API_KEYS_DB) as f:
            return json.load(f)
    except:
        return {}

def save_api_keys(keys):
    with open(API_KEYS_DB, 'w') as f:
        json.dump(keys, f, indent=2)

def generate_random_key(prefix="API_"):
    return prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def create_github_token(scope="repo"):
    if not GITHUB_TOKEN:
        return None
    url = "https://api.github.com/authorizations"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "scopes": [scope],
        "note": f"Auto-generated token {random.randint(1000,9999)}"
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        if r.status_code == 201:
            token = r.json()["token"]
            keys = load_api_keys()
            keys.setdefault("github", []).append(token)
            save_api_keys(keys)
            return token
    except:
        pass
    return None

def create_openai_key():
    new_key = generate_random_key("sk-")
    keys = load_api_keys()
    keys.setdefault("openai", []).append(new_key)
    save_api_keys(keys)
    return new_key
