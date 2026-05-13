```python
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

# ===== FLASK =====

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
    )

    return DATA

# ===== DATA =====

async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"] = update.message.text

    keyboard = [
        ["DEA", "GLORIA"],
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

async def nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nome"] = update.message.text

    keyboard = [
        ["POST INFORMA + ARTICOLO"],
        ["GRAFICA"],
        ["VIDEO REEL"],
        ["FOTO"],
        ["INTERVISTA"],
        ["ARTICOLO INTERNO"],
        ["POST"],
        ["BREAKING NEWS"],
        ["AGGIORNAMENTO SITO"],
        ["STORIES"],
        ["RADIO"],
        ["EXTRA"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🛠 Seleziona tipo lavoro:",
        reply_markup=reply_markup
    )

    return TIPO

# ===== TIPO =====

async def tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tipo"] = update.message.text

    keyboard = [
        ["PUBBLICATO"],
        ["PRONTO"],
        ["IN LAVORAZIONE"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "📌 Seleziona stato:",
        reply_markup=reply_markup
    )

    return STATO

# ===== STATO =====

async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stato"] = update.message.text

    await update.message.reply_text(
        "📝 Scrivi eventuali note:",
        reply_markup=ReplyKeyboardRemove()
    )

    return NOTE

# ===== NOTE =====

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note_value = update.message.text

    data_value = context.user_data["data"]
    nome_value = context.user_data["nome"]
    tipo_value = context.user_data["tipo"]
    stato_value = context.user_data["stato"]

    sheet.append_row([
        data_value,
        nome_value,
        tipo_value,
        stato_value,
        note_value
    ])

    await update.message.reply_text(
        "✅ Dati inseriti nel Google Sheet!"
    )

    return ConversationHandler.END

# ===== CANCEL =====

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Operazione annullata."
    )

    return ConversationHandler.END

# ===== MAIN =====

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("avvia", start),
        CommandHandler("start", start)
    ],

    states={

        DATA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, data)
        ],

        NOME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, nome)
        ],

        TIPO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, tipo)
        ],

        STATO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, stato)
        ],

        NOTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, note)
        ],
    },

    fallbacks=[
        CommandHandler("cancel", cancel)
    ]
)

app.add_handler(conv_handler)

print("BOT AVVIATO...")

app.run_polling()
```
