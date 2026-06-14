#!/usr/bin/env python3
from telegram import Update
from telegram.ext import Application, CommandHandler
import sqlite3, os
DB = os.path.expanduser("~/ia_shared/db/nexus.db")
async def start(update, context):
    await update.message.reply_text("Bienvenue ! Tapez /ventes")
async def ventes(update, context):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT SUM(montant) FROM ventes")
    total = c.fetchone()[0] or 0
    await update.message.reply_text(f"💰 Revenu total : {total} USD")
app = Application.builder().token("VOTRE_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ventes", ventes))
app.run_polling()
