#!/usr/bin/env python3
import os, sys, time, sqlite3
sys.path.append(os.path.expanduser("~/ia_shared"))
from ia_nexus import ConfigManager
# Simulé – à connecter à IMAP si besoin
print("Scanner PayPal actif (simulation)")
while True: time.sleep(120)
