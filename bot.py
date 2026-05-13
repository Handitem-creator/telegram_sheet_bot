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

from oauth2client.service_account import ServiceAccountCredentials

# ===== GOOGLE SHEETS =====

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ===== CREDENTIALS RENDER =====

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
    )

    return DATA

# ===== DATA =====

async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"] = update.message.text

    keyboard = [
        ["DEA", "GLORA"],
        ["ALESSANDRO", "MARCO"],
        ["PAOLO", "LUCA"],
        ["TUTTI"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👤 Seleziona il nome:",
        reply_markup=reply_markup
    )

    return NOME

# ===== NOME =====
app.run_polling()