from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

import gspread
import os
import json
import threading

from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials

# ===== FLASK PORTA WEB =====

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return 'Bot online!'


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)


threading.Thread(target=run_web).start()

# ===== GOOGLE SHEETS =====

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

google_credentials = json.loads(
    os.getenv("GOOGLE_CREDENTIALS")
)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_credentials,
    scope
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(
    "10P2g8kA15PLo6pFwDCHddoMmHrSrmFcj3yaLvhwP2Qc"
)

sheet = spreadsheet.sheet1

# ===== TOKEN =====

TOKEN = os.getenv("TOKEN")

# ===== STATI =====

DATA, NOME, TIPO, STATO, NOTE = range(5)

# ===== START =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Inserisci la data:"
app.run_polling()