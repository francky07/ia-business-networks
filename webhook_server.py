from flask import Flask, request, jsonify
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        app.logger.info(f"Reçu : {data}")
        # Ici vous pouvez traiter les données (vendre, stocker, etc.)
        # Pour l'instant, on simule une vente réussie
        items = data.get('items', [])
        gain = len(items) * 0.01
        return jsonify({"status": "success", "gain": gain}), 200
    except Exception as e:
        app.logger.error(f"Erreur : {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
