import os
import telebot
import uuid
from datetime import datetime
from supabase import create_client

# --- READ FROM ENVIRONMENT VARIABLES ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
# TARGET_CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002650324099"))  # Optional fallback

TARGET_CHANNEL_ID = -1002650324099  # Use -100 prefix for private channels

bot = telebot.TeleBot(BOT_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- STORE MEDIA TO SUPABASE ---
def save_media_to_supabase(file_id, media_type, trigger_id):
    try:
        data = {
            "file_id": file_id,
            "media_type": media_type,
            "trigger_id": trigger_id,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("media_store").insert(data).execute()
        return result
    except Exception as e:
        print("❌ Error saving to Supabase:", e)
        return None

# --- RETRIEVE MEDIA BY TRIGGER ID ---
def get_media_by_trigger_id(trigger_id):
    try:
        result = supabase.table("media_store").select("*").eq("trigger_id", trigger_id).limit(1).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print("❌ Error fetching from Supabase:", e)
        return None

# --- HANDLE PHOTO/VIDEO FROM CHANNEL ---
@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    if message.chat.id != TARGET_CHANNEL_ID:
        return  # Ignore messages from outside the target channel

    media_type = message.content_type
    trigger_id = str(uuid.uuid4())[:8]  # Short and unique

    if media_type == 'photo':
        file_id = message.photo[-1].file_id
    elif media_type == 'video':
        file_id = message.video.file_id
    else:
        return

    result = save_media_to_supabase(file_id, media_type, trigger_id)

    if result:
        bot.reply_to(
            message,
            f"✅ Media saved!\n🔗 Shareable Link:\nhttps://t.me/TechieMonkBot?start={trigger_id}",
            parse_mode="Markdown"
        )

    else:
        bot.reply_to(message, "❌ Failed to save media.")

# --- HANDLE /get TRIGGER COMMAND ---
@bot.message_handler(commands=['get'])
def handle_get_command(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            bot.reply_to(message, "⚠️ Usage: `/get <trigger_id>`", parse_mode="Markdown")
            return

        trigger_id = parts[1]
        media = get_media_by_trigger_id(trigger_id)

        if not media:
            bot.reply_to(message, "❌ No media found for that trigger ID.")
            return

        file_id = media["file_id"]
        media_type = media["media_type"]

        if media_type == "photo":
            bot.send_photo(message.chat.id, file_id)
        elif media_type == "video":
            bot.send_video(message.chat.id, file_id)
        else:
            bot.reply_to(message, "⚠️ Unsupported media type stored.")
    except Exception as e:
        print("❌ Error in /get handler:", e)
        bot.reply_to(message, "⚠️ An error occurred. Please try again.")



@bot.message_handler(commands=['start'])
def handle_start_command(message):
    parts = message.text.strip().split()
    if len(parts) == 2:
        trigger_id = parts[1]
        media = get_media_by_trigger_id(trigger_id)

        if not media:
            bot.reply_to(message, "❌ No media found for that trigger ID.")
            return

        file_id = media["file_id"]
        media_type = media["media_type"]

        if media_type == "photo":
            bot.send_photo(message.chat.id, file_id)
        elif media_type == "video":
            bot.send_video(message.chat.id, file_id)
        else:
            bot.reply_to(message, "⚠️ Unsupported media type.")
    else:
        bot.send_message(message.chat.id, "👋 Welcome to TechieMonkBot! Send me a trigger ID or use /get.")



# --- START POLLING ---
print("🤖 Bot is running...")
bot.infinity_polling()
