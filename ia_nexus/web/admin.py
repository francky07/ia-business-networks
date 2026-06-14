from flask import Flask, render_template_string
import sqlite3, os
app = Flask(__name__)
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0")
    emails = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(montant),0) FROM ventes")
    revenue = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leads")
    leads = c.fetchone()[0]
    conn.close()
    html = f"<h1>IA Nexus Admin</h1><p>Emails en stock: {emails}</p><p>Revenu total: {revenue} USD</p><p>Leads: {leads}</p>"
    return html
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
