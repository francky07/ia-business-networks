#!/usr/bin/env python3
import requests, re, sqlite3, time, os
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
SITES = ["https://www.leboncoin.fr/offres/", "https://www.freelance-info.fr/annonces"]
def extract_emails(html): return set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html))
def main():
    while True:
        for url in SITES:
            try:
                r = requests.get(url, timeout=10)
                emails = extract_emails(r.text)
                conn = sqlite3.connect(DB)
                for e in emails:
                    conn.execute("INSERT OR IGNORE INTO leads (email, source, date_ajout) VALUES (?,?,?)", (e, url, int(time.time())))
                conn.commit()
                conn.close()
                print(f"{len(emails)} leads depuis {url}")
            except: pass
        time.sleep(600)
if __name__ == '__main__':
    main()
