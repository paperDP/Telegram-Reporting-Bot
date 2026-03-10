import os
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

# Load secrets from .env file - essential for security
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_ID", 0))

# Standard logging setup
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# --- Database Setup ---
# I prefer keeping DB logic close to the start to ensure tables exist
db_conn = sqlite3.connect('bot_data.db')
db = db_conn.cursor()

def setup_db():
    db.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, 
                   reg_date TEXT, user_id INTEGER, role TEXT)''')
    
    db.execute('''CREATE TABLE IF NOT EXISTS media_logs
                  (id INTEGER PRIMARY KEY, file_id TEXT, timestamp TEXT)''')
    db_conn.commit()

setup_db()

# Ensure directories for storage exist
os.makedirs("uploads/photos", exist_ok=True)
os.makedirs("uploads/audios", exist_ok=True)

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    u_id = message.from_user.id
    u_name = message.from_user.username
    u_first = message.from_user.first_name
    
    # Simple role check
    role = "admin" if u_id == ADMIN_USER_ID else "user"

    # Save new user if not in DB
    db.execute('SELECT id FROM users WHERE user_id = ?', (u_id,))
    if not db.fetchone():
        db.execute(
            'INSERT INTO users (first_name, username, reg_date, user_id, role) VALUES (?, ?, ?, ?, ?)',
            (u_first, u_name, str(datetime.now()), u_id, role)
        )
        db_conn.commit()

        # Alert me when someone new shows up
        if role != "admin":
            alert = (f"🚀 <b>New User Spotted!</b>\n"
                     f"ID: <code>{u_id}</code>\n"
                     f"Name: {u_first}\n"
                     f"User: @{u_name}")
            await bot.send_message(ADMIN_USER_ID, alert, parse_mode="HTML")

    if role == "admin":
        await message.reply("Welcome back, Boss. Waiting for reports.")
    else:
        await message.reply("Hey! This is a news tip bot. Send me any text, photos, or videos you want to share.")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text_reports(message: types.Message):
    # Skip processing if admin is just typing
    if message.from_user.id == ADMIN_USER_ID:
        return

    # Forward to admin
    report = (f"📩 <b>New Text Report:</b>\n\n{message.text}\n\n"
              f"From: @{message.from_user.username} (ID: <code>{message.from_user.id}</code>)")
    
    await bot.send_message(ADMIN_USER_ID, report, parse_mode="HTML")
    await message.answer("✅ Got it! Thanks for the tip. Send more if you have any.")

@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.AUDIO])
async def handle_media_reports(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        return

    u_info = f"From: @{message.from_user.username} (ID: <code>{message.from_user.id}</code>)"
    
    # Handle Photo
    if message.content_type == types.ContentType.PHOTO:
        f_id = message.photo[-1].file_id
        # Saving local copy just in case
        photo_info = await bot.get_file(f_id)
        save_path = os.path.join("uploads/photos", f"{f_id}.jpg")
        await bot.download_file(photo_info.file_path, save_path)
        
        await bot.send_photo(ADMIN_USER_ID, f_id, caption=f"📸 Photo Report\n{u_info}\n\nCaption: {message.caption or 'None'}", parse_mode="HTML")

    # Handle Video
    elif message.content_type == types.ContentType.VIDEO:
        await bot.send_video(ADMIN_USER_ID, message.video.file_id, caption=f"🎬 Video Report\n{u_info}", parse_mode="HTML")

    # Handle Audio
    elif message.content_type == types.ContentType.AUDIO:
        await bot.send_audio(ADMIN_USER_ID, message.audio.file_id, caption=f"🎵 Audio Report\n{u_info}", parse_mode="HTML")

    # Log file ID to DB to prevent duplicates if needed
    db.execute('INSERT INTO media_logs (file_id, timestamp) VALUES (?, ?)', (message.md5_digest or "no_hash", str(datetime.now())))
    db_conn.commit()
    
    await message.answer("✅ Media received! Our editors will check it out.")

if __name__ == '__main__':
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)