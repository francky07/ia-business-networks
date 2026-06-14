#!/usr/bin/env python3
import telebot
TOKEN = 'VOTRE_TOKEN'
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def start(msg): bot.reply_to(msg, 'Bot IA NetSolutions')
bot.infinity_polling()
