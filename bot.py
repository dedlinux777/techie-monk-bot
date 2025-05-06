import os
import uuid
import psycopg2
from telebot import TeleBot, types
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = TeleBot(BOT_TOKEN)

# DB connection
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Handle media uploads from your private channel
@bot.message_handler(content_types=['video', 'photo'], chat_types=['channel'])
def handle_media(message):
    if message.content_type == 'video':
        file_id = message.video.file_id
        media_type = 'video'
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        media_type = 'photo'
    else:
        return

    trigger_id = str(uuid.uuid4())[:8]  # short unique id
    uploaded_at = datetime.now()

    # Save metadata to Supabase
    try:
        cur.execute("""
            INSERT INTO media_store (file_id, media_type, trigger_id, uploaded_at)
            VALUES (%s, %s, %s, %s)
        """, (file_id, media_type, trigger_id, uploaded_at))
        conn.commit()
    except Exception as e:
        print(f"DB insert failed: {e}")
        return

    bot.send_message(message.chat.id,
        f"Media saved! Share this link: /get_{trigger_id}"
    )

# Handle user command to fetch media
@bot.message_handler(commands=['get'])
def handle_get_command(message):
    cmd = message.text.strip().split('_')
    if len(cmd) < 2:
        bot.reply_to(message, "Invalid command format.")
        return

    trigger_id = cmd[1]
    cur.execute("SELECT file_id, media_type FROM media_store WHERE trigger_id=%s", (trigger_id,))
    result = cur.fetchone()

    if result:
        file_id, media_type = result
        if media_type == 'photo':
            bot.send_photo(message.chat.id, file_id)
        elif media_type == 'video':
            bot.send_video(message.chat.id, file_id)
    else:
        bot.reply_to(message, "No media found with that trigger.")

# /start, /info, /status commands
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, f"Hello {message.from_user.first_name}")

@bot.message_handler(commands=['info'])
def info_cmd(message):
    bot.reply_to(message, "I am a bot here to help.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    bot.reply_to(message, "I am active!")

print("Bot is running...")
bot.polling()
