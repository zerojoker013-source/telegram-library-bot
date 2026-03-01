import os
import asyncio
import sqlite3
from rapidfuzz import process
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext

# ====== קריאה למשתנים סודיים ======
API_ID = os.getenv('30420089')              # מספר שהתקבלת מ‑Telegram
API_HASH = os.getenv('2c2c383326d0b8d234ea8e6cb2cecdfa')          # המפתח שהתקבלת מ‑Telegram
BOT_TOKEN = os.getenv('7984760860:AAEcv2BhWyKsKzAaItG7YGE__qrUJEs2SEQ')        # הטוקן של הבוט
CHANNELS = os.getenv('+oRjw7G6dKk9jYzk8', '+FcYMH_laS2c3NWQ0').split(',')  # רשימת יוזרים מופרדים בפסיקים

# ====== מסד נתונים ======
DB_NAME = 'files.db'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS files
             (id INTEGER PRIMARY KEY, file_name TEXT, file_id TEXT, type TEXT)''')
conn.commit()

# ====== פונקציה לחיפוש קבצים ======
def search_files(query):
    c.execute('SELECT file_name, file_id, type FROM files')
    results = c.fetchall()
    matches = process.extract(query, [r[0] for r in results], limit=10)
    final = []
    for match in matches:
        idx = match[2]
        final.append(results[idx])
    return final

# ====== שליחת תוצאות חיפוש ======
async def search(update: Update, context: CallbackContext):
    query = update.message.text
    results = search_files(query)
    if not results:
        await update.message.reply_text("לא נמצאו קבצים תואמים.")
        return
    for name, file_id, ftype in results:
        await update.message.reply_document(document=file_id, filename=name)

# ====== הפעלת הבוט ======
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    print(f'Bot started. Connected channels: {CHANNELS}')
    await app.run_polling()

asyncio.run(main())
