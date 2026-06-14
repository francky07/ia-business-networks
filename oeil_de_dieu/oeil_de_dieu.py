#!/usr/bin/env python3
import time, subprocess
print("Œil de Dieu – surveillance active")
while True:
    subprocess.run(["tmux", "ls"], capture_output=True)
    time.sleep(300)
