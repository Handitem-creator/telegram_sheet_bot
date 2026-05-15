import os
import json
import threading
import gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# --- FLASK CONFIG ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- GOOGLE SHEETS CONFIG ---
def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_raw = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(creds_raw)
    
    # Fix per le chiavi private che contengono \n
    if "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Inizializza subito Google Sheets
client = get_gsheet_client()
spreadsheet = client.open_by_key("10P2g8kA15PLo6pFwDCHddoMmHrSrmFcj3yaLvhwP2Qc")
sheet = spreadsheet.sheet1

# --- BOT LOGIC ---
TOKEN = os.getenv("TOKEN")
DATA, NOME, TIPO, STATO, NOTE = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Inserisci la data:")
    return DATA

async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"] = update.message.text
    kb = [["DEA", "GLORIA"], ["ALESSANDRO", "MARCO"], ["PAOLO", "LUCA"], ["TUTTI"]]
    await update.message.reply_text("👤 Seleziona il nome:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return NOME

async def nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nome"] = update.message.text
    kb = [["POST INFORMA + ARTICOLO", "GRAFICA"], ["VIDEO REEL", "FOTO"], ["INTERVISTA", "ARTICOLO INTERNO"], ["POST", "BREAKING NEWS"], ["AGGIORNAMENTO SITO", "STORIES"], ["RADIO", "EXTRA"]]
    await update.message.reply_text("🛠 Seleziona tipo lavoro:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return TIPO

async def tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tipo"] = update.message.text
    kb = [["PUBBLICATO"], ["PRONTO"], ["IN LAVORAZIONE"]]
    await update.message.reply_text("📌 Seleziona stato:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return STATO

async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stato"] = update.message.text
    await update.message.reply_text("📝 Scrivi eventuali note:", reply_markup=ReplyKeyboardRemove())
    return NOTE

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n_val = update.message.text
    d = context.user_data
    try:
        sheet.append_row([d["data"], d["nome"], d["tipo"], d["stato"], n_val])
        await update.message.reply_text("✅ Dati inseriti nel Google Sheet!")
    except Exception as e:
        await update.message.reply_text(f"❌ Errore: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Annullato.")
    return ConversationHandler.END

# --- MAIN ---
if __name__ == "__main__":
    # 1. Fai partire Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Configura e fai partire il Bot (questo blocca il thread principale, il che è bene)
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("avvia", start)],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, data)],
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nome)],
            TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, tipo)],
            STATO: [MessageHandler(filters.TEXT & ~filters.COMMAND, stato)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, note)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(conv)
    
    print("🚀 BOT AVVIATO...")
    app.run_polling()