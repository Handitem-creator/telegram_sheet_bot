import os
import json
import threading
import gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
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

# ===== CONFIGURAZIONE FLASK (Keep-alive) =====
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return 'Bot online!'

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# Avvio del server Flask in un thread separato
threading.Thread(target=run_web, daemon=True).start()

# ===== CONFIGURAZIONE GOOGLE SHEETS =====
def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Carica credenziali da variabile d'ambiente
    creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Inizializzazione foglio
client = get_gsheet_client()
spreadsheet = client.open_by_key("10P2g8kA15PLo6pFwDCHddoMmHrSrmFcj3yaLvhwP2Qc")
sheet = spreadsheet.sheet1

# ===== CONFIGURAZIONE BOT =====
TOKEN = os.getenv("TOKEN")

# Stati della conversazione
DATA, NOME, TIPO, STATO, NOTE = range(5)

# --- CALLBACKS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 **Benvenuto!**\nInserisci la data del lavoro (es. 24/05/2024):",
        parse_mode="Markdown"
    )
    return DATA

async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"] = update.message.text
    keyboard = [
        ["DEA", "GLORIA"],
        ["ALESSANDRO", "MARCO"],
        ["PAOLO", "LUCA"],
        ["TUTTI"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("👤 Seleziona il nome:", reply_markup=reply_markup)
    return NOME

async def nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nome"] = update.message.text
    keyboard = [
        ["POST INFORMA + ARTICOLO", "GRAFICA"],
        ["VIDEO REEL", "FOTO"],
        ["INTERVISTA", "ARTICOLO INTERNO"],
        ["POST", "BREAKING NEWS"],
        ["AGGIORNAMENTO SITO", "STORIES"],
        ["RADIO", "EXTRA"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("🛠 Seleziona il tipo di lavoro:", reply_markup=reply_markup)
    return TIPO

async def tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tipo"] = update.message.text
    keyboard = [
        ["PUBBLICATO"],
        ["PRONTO"],
        ["IN LAVORAZIONE"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📌 Seleziona lo stato attuale:", reply_markup=reply_markup)
    return STATO

async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stato"] = update.message.text
    await update.message.reply_text(
        "📝 Scrivi eventuali note (o scrivi 'nessuna'):",
        reply_markup=ReplyKeyboardRemove()
    )
    return NOTE

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note_value = update.message.text
    user_data = context.user_data

    await update.message.reply_text("⏳ Salvataggio in corso su Google Sheets...")

    try:
        # Append row al foglio
        sheet.append_row([
            user_data["data"],
            user_data["nome"],
            user_data["tipo"],
            user_data["stato"],
            note_value
        ])
        await update.message.reply_text("✅ Dati inseriti con successo!")
    except Exception as e:
        await update.message.reply_text(f"❌ Errore durante il salvataggio: {e}\n\nAssicurati che le API siano attive.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Operazione annullata.", 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# --- MAIN ---

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("avvia", start)
        ],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, data)],
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nome)],
            TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, tipo)],
            STATO: [MessageHandler(filters.TEXT & ~filters.COMMAND, stato)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, note)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    print("🚀 BOT AVVIATO...")
    application.run_polling()