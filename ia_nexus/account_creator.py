#!/usr/bin/env python3
import random, string, sqlite3, time, os
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
def generate_twitter_account():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@tempmail.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return ('twitter', username, password, 0.05)
def main():
    while True:
        type_acc, login, pwd, price = generate_twitter_account()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO comptes (type, identifiant, mot_de_passe, date_creation, vendu, prix) VALUES (?,?,?,?,?,?)",
                  (type_acc, login, pwd, int(time.time()), 0, price))
        conn.commit()
        conn.close()
        print(f"Compte {type_acc} créé : {login}")
        time.sleep(120)
if __name__ == '__main__':
    main()
