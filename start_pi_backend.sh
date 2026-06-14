#!/data/data/com.termux/files/usr/bin/bash
cd ~/ia_web
pip install flask flask_cors requests
python pi_backend.py &
echo "✅ Backend Pi Network démarré sur http://localhost:5001"
