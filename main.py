import os
import time
import telebot
from openai import OpenAI

# Токен твоего Telegram-бота
TELEGRAM_TOKEN = "8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Безопасно подтягиваем ключ из переменных окружения (GitHub Secrets)
API_KEY = os.getenv("GROQ_API_KEY")

# Инициализируем клиента Groq
ai_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=API_KEY if API_KEY else "dummy_key"
)

# Юзернейм твоего бота для корректного отлова упоминаний в группах
BOT_USERNAME = "assistantasil_bot".lower()

def get_ai_response(prompt_text):
    """Запрос к нейросети для сложных вопросов"""
    if not API_KEY:
        return "Ошибка: API-ключ не найден в переменных окружения GitHub Secrets!"
    
    try:
        completion = ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Мощная модель Groq
            messages=[
                {"role": "system", "content": "Ты крутой, дерзкий и умный помощник в Телеграм-чате. Отвечай интересно, по делу, но с вайбом."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Ошибка запроса к ИИ: {e}")
        return f"Сбой нейросети: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.id == bot.get_me().id:
        return

    chat_type = message.chat.type
    text = message.text.lower() if message.text else ""

    # 1. Эхо-команда («скажи» / «повтори»)
    if text.startswith(('скажи ', 'повтори ')):
        text_to_repeat = message.text.split(maxsplit=1)
        if len(text_to_repeat) > 1:
            repeat_text = text_to_repeat[1]
            try:
                time.sleep(0.2)
                if chat_type != 'private':
                    bot.reply_to(message, repeat_text)
                else:
                    bot.send_message(message.chat.id, repeat_text)
            except Exception as e:
                print(f"Ошибка эхо: {e}")
        else:
            bot.reply_to(message, "А что сказать-то? Напиши после команды.")
        return

    # 2. В личке общаемся с ИИ
    if chat_type == 'private':
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            ai_reply = get_ai_response(message.text)
            time.sleep(0.2)
            bot.send_message(message.chat.id, ai_reply)
        except Exception as e:
            print(f"Ошибка ЛС: {e}")
        return

    # 3. В группах отвечаем только по упоминанию или реплаю
    is_mentioned = f"@{BOT_USERNAME}" in text
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id

    if is_mentioned or is_reply_to_bot:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            clean_prompt = message.text.replace(f"@{BOT_USERNAME}", "").strip()
            ai_reply = get_ai_response(clean_prompt if clean_prompt else "Привет! Че как?")
            time.sleep(0.2)
            bot.reply_to(message, ai_reply)
        except Exception as e:
            print(f"Ошибка в группе: {e}")
        return

if __name__ == "__main__":
    bot.remove_webhook()
    print("Бот запущен в режиме чистого ИИ через секреты!")
    bot.infinity_polling()
    
