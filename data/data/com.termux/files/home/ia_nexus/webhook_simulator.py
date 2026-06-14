#!/usr/bin/env python3
import sqlite3, time, os, random
from flask import Flask, request
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
app = Flask(__name__)
@app.route('/paypal-webhook', methods=['POST'])
def handle_payment():
    data = request.json
    if data and data.get('event_type') == 'PAYMENT.CAPTURE.COMPLETED':
        amount = data.get('amount', 0)
        # Mettre à jour la base (marquer les emails non vendus comme livrés)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("UPDATE emails SET vendu=2 WHERE vendu=0")
        conn.commit()
        conn.close()
        print(f"Paiement de {amount} USD reçu – emails livrés.")
        return "OK", 200
    return "Ignored", 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
