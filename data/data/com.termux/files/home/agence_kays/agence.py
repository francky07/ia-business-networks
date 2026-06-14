#!/usr/bin/env python3
import sys, os, random, time
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import NexusDB
while True:
    email = f"user{random.randint(100000,999999)}@guerrillamail.com"
    NexusDB.add_email(email, "agence_kays")
    print(f"✅ Email produit: {email}")
    time.sleep(60)
