#!/usr/bin/env python3
import subprocess, time, threading, os
def check_tmux():
    required = ["agence_kays","ventes","ia_net","nexus_brain"]
    out = subprocess.run(["tmux","ls"], capture_output=True, text=True).stdout
    for s in required:
        if s not in out:
            subprocess.run(["tmux","new-session","-d","-s",s,"python ~/"+s+".py"], shell=True)
    time.sleep(30)
for _ in range(300):
    threading.Thread(target=check_tmux, daemon=True).start()
while True: time.sleep(60)
