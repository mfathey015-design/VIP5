import os, requests, base64, json, telebot, time, subprocess
from telebot import types

# --- إعدادات الحساب المحدثة ---
GITHUB_TOKEN = "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"
GITHUB_USER = "mfathey015-design"
REPO_NAME = "VIP5" 
TELEGRAM_BOT_TOKEN = "8617451183:AAEycqcq4CgfUUUwucIAeB-87wngIYdPOUI"
DEV_URL = "https://t.me/mfathey466"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def prevent_sleep():
    """تفعيل منع السكون (تعمل في بيئات معينة)"""
    try:
        subprocess.run(["termux-wake-lock"], check=True)
    except:
        pass

def upload_to_github(content, file_name):
    """رفع الملف لجيتهاب والحصول على الرابط المباشر"""
    clean_name = file_name.replace(" ", "%20")
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{clean_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    res_get = requests.get(url, headers=headers)
    sha = res_get.json().get('sha') if res_get.status_code == 200 else None
    
    encoded_content = base64.b64encode(content).decode('utf-8')
    data = {
        "message": f"Cloud Update/Upload {clean_name}",
        "content": encoded_content,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
        
    res_put = requests.put(url, data=json.dumps(data), headers=headers)
    if res_put.status_code in [200, 201]:
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{clean_name}"
        return raw_url, bool(sha)
    return None, False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="👨‍💻 مراسلة المطور", url=DEV_URL))
    
    welcome_text = (
        "مرحباً بكم في بوت المطور محمد المصري لرفع الحماية أونلاين\n"
        "━━━━━━━━━━━━━━\n"
        "أرسل ملف الـ ZIP الآن ليتم رفعه إلى مستودعك."
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if not message.document.file_name.lower().endswith('.zip'):
        bot.reply_to(message, "⚠️ يرجى إرسال ملفات ZIP فقط.")
        return
    
    msg = bot.reply_to(message, "⏳ جاري رفع الملف وتحديث البيانات على GitHub...")
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_base_name = os.path.splitext(message.document.file_name)[0]
        
        dynamic_version = int(time.time()) % 10000 
        
        # 1. رفع ملف ZIP
        zip_url, is_update = upload_to_github(downloaded_file, f"{file_base_name}.zip")
        
        # 2. رفع ملف JSON للتحديث التلقائي
        json_data = {"bypassVersion": dynamic_version}
        json_content = json.dumps(json_data, indent=2).encode('utf-8')
        json_url, _ = upload_to_github(json_content, f"{file_base_name}.json")
        
        if zip_url and json_url:
            bot.delete_message(message.chat.id, msg.message_id)
            
            caption_text = (
                f"{'✅ تم تحديث الملف' if is_update else '✅ تم الرفع بنجاح'}\n"
                f"📦 إصدار الحماية: {dynamic_version}\n"
                "━━━━━━━━━━━━━━\n"
                f"🔗 رابط ZIP المباشر:\n{zip_url}\n\n"
                f"🔗 رابط JSON المباشر:\n{json_url}"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="👨‍💻 مراسلة المطور", url=DEV_URL))
            bot.send_document(message.chat.id, message.document.file_id, caption=caption_text, reply_markup=markup)
        else:
            bot.edit_message_text("❌ فشل الرفع. تأكد من أن اسم المستودع (REPO_NAME) صحيح وموجود فعلياً.", message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

if __name__ == '__main__':
    prevent_sleep()
    print("\n\033[1;36m🚀 البوت المصري يعمل الآن بنجاح...\033[0m\n")
    bot.infinity_polling()
