#built-in modules
import sqlite3

#needs to install using pip
import telebot
from flask import Flask, request

#local package import
from cowin import config

url = f'https://{config.HOST_USERNAME}.pythonanywhere.com/{config.SECRET_KEY}'

#Bot Initialization
bot = telebot.TeleBot(config.BOT_TOKEN, threaded=False, parse_mode='HTML')
bot.remove_webhook()
bot.set_webhook(url=url)

conn = sqlite3.connect(config.DB_FILE, check_same_thread=False)
cur = conn.cursor()

try:
    with conn:
        cur.execute('create table users (id integer primary key, username text, date text, district default None, age default None, vaccine default None, fee default None, dose default None, pincode default None)')
except:
    pass

#require to connect files with each other
from cowin import bot_handler, func, log

#For running without polling method
app = Flask(__name__)

@app.route('/' + config.SECRET_KEY, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(
        request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def home():
    return f'<h1>Bot Running at <a href="https://t.me/{config.BOT_USERNAME}">@{config.BOT_USERNAME}</a> on Telegram</h1>'