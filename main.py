import os
import random
import time
import telebot
from openai import OpenAI

TELEGRAM_TOKEN = "8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Инициализируем клиента Groq
groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

BOT_USERNAME = "Assistantasil_bot".lower()

def get_ai_response(prompt_text):
    """Функция для запроса к умному ИИ через Groq"""
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты крутой, дерзкий и умный помощник в Телеграм-чате. Отвечай интересно, по делу, но с вайбом."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Ошибка запроса к Groq AI: {e}")
        return "Что-то мои нейросети приуныли, повтори вопрос."

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

    # 2. Если личка — общаемся с умным ИИ от Groq
    if chat_type == 'private':
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            ai_reply = get_ai_response(message.text)
            time.sleep(0.2)
            bot.send_message(message.chat.id, ai_reply)
        except Exception as e:
            print(f"Ошибка ЛС ИИ: {e}")
        return

    # 3. В группах отвечаем ТОЛЬКО если есть упоминание @username или реплай на сообщение бота
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
            print(f"Ошибка ИИ в группе: {e}")
        return

    # Обычные сообщения в группах теперь просто игнорируются (никакого рандомного спама)

if __name__ == "__main__":
    bot.remove_webhook()
    print("Бот переключен в режим умного помощника (без фонового спама фразами)!")
    bot.infinity_polling()
    
