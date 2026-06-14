#!/usr/bin/env python3
import requests
print("Client hub (simulation)")
while True:
    try: requests.get("http://localhost:5003"); print("Hub accessible")
    except: print("Hub injoignable")
    time.sleep(60)
