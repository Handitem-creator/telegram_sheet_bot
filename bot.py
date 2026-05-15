import os
import json
import threading
import gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# --- 1. FLASK (Keep-alive per Render) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return 'Bot is alive!'

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 2. FUNZIONE SALVATAGGIO (Connessione "On-Demand") ---
def save_to_sheet(data_list):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(creds_json)
    
    if "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # Sostituisci qui il tuo ID foglio se necessario
    sheet = client.open_by_key("10P2g8kA15PLo6pFwDCHddoMmHrSrmFcj3yaLvhwP2Qc").sheet1
    sheet.append_row(data_list)

# --- 3. BOT LOGIC ---
TOKEN = os.getenv("TOKEN")
DATA, NOME, TIPO, STATO, NOTE = range(5)

async def start_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("📅 Inserisci la data:")
    return DATA

async def handle_data(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data["data"] = u.message.text
    kb = [["DEA", "GLORIA"], ["ALESSANDRO", "MARCO"], ["PAOLO", "LUCA"], ["TUTTI"]]
    await u.message.reply_text("👤 Nome:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return NOME

async def handle_nome(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data["nome"] = u.message.text
    kb = [["POST", "GRAFICA"], ["VIDEO", "FOTO"], ["ARTICOLO", "EXTRA"]]
    await u.message.reply_text("🛠 Lavoro:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return TIPO

async def handle_tipo(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data["tipo"] = u.message.text
    kb = [["PUBBLICATO", "PRONTO"], ["IN LAVORAZIONE"]]
    await u.message.reply_text("📌 Stato:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return STATO

async def handle_stato(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data["stato"] = u.message.text
    await u.message.reply_text("📝 Note:", reply_markup=ReplyKeyboardRemove())
    return NOTE

async def handle_note(u: Update, c: ContextTypes.DEFAULT_TYPE):
    try:
        d = c.user_data
        # Chiamiamo la connessione solo ora
        save_to_sheet([d["data"], d["nome"], d["tipo"], d["stato"], u.message.text])
        await u.message.reply_text("✅ Salvato su Google Sheets!")
    except Exception as e:
        await u.message.reply_text(f"❌ Errore durante il salvataggio: {e}")
    return ConversationHandler.END

async def cancel(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("Annullato.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- 4. MAIN ---
if __name__ == "__main__":
    print("--- AVVIO SISTEMA ---")
    
    # Avvia Flask
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()
    print("1. Flask avviato in background")

    # Avvia Bot
    print("2. Inizializzazione Bot...")
    bot_app = ApplicationBuilder().token(TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start_cmd), CommandHandler("avvia", start_cmd)],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_data)],
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nome)],
            TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tipo)],
            STATO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stato)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_note)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    bot_app.add_handler(conv)
    print("3. ✅ BOT PRONTO. Vai su Telegram!")
    bot_app.run_polling()