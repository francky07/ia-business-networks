from flask import Flask, render_template_string
import sqlite3, os, subprocess

app = Flask(__name__)
DB = os.path.expanduser("~/ia_shared/db/nexus.db")

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emails WHERE vendu=0")
    emails = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leads")
    leads = c.fetchone()[0]
    c.execute("SELECT SUM(montant) FROM ventes")
    revenue = c.fetchone()[0] or 0
    conn.close()
    tmux_sessions = subprocess.getoutput("tmux ls")
    return render_template_string('''
        <h1>IA Nexus Dashboard</h1>
        <p>Emails en stock: {{ emails }}</p>
        <p>Leads collectés: {{ leads }}</p>
        <p>Revenu total: {{ revenue }} USD</p>
        <pre>{{ tmux_sessions }}</pre>
    ''', emails=emails, leads=leads, revenue=revenue, tmux_sessions=tmux_sessions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
