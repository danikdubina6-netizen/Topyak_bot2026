import os
import random
import time
import requests
import telebot

TELEGRAM_TOKEN = "8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4"
# Лучше вынести в секреты GitHub Actions, но пока для теста можно и сюда:
OPENROUTER_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
BOT_USERNAME = "Assistantasil_bot".lower()

def get_openrouter_response(prompt_text):
    """Функция для запроса к ИИ через OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com",  # Обязательный заголовок для OpenRouter
        "X-Title": "Topyak Bot",               # Название твоего проекта
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-4o",  # Можешь поменять на любую другую, например "deepseek/deepseek-chat" или "google/gemini-flash-1.5"
        "messages": [
            {
                "role": "system",
                "content": "Ты крутой, дерзкий и умный помощник в Телеграм-чате. Отвечай интересно, по делу, но с вайбом."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Ответ OpenRouter с ошибкой: {result}")
            return "Что-то пошло не так, нейросеть приуныла."
    except Exception as e:
        print(f"Ошибка запроса к OpenRouter: {e}")
        return "Ошибка соединения с ИИ."

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

    # 2. В личке общаемся с ИИ через OpenRouter
    if chat_type == 'private':
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            ai_reply = get_openrouter_response(message.text)
            time.sleep(0.2)
            bot.send_message(message.chat.id, ai_reply)
        except Exception as e:
            print(f"Ошибка ЛС ИИ: {e}")
        return

    # 3. В группах отвечаем только при упоминании или реплае
    is_mentioned = f"@{BOT_USERNAME}" in text
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id

    if is_mentioned or is_reply_to_bot:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            clean_prompt = message.text.replace(f"@{BOT_USERNAME}", "").strip()
            ai_reply = get_openrouter_response(clean_prompt if clean_prompt else "Привет! Че как?")
            time.sleep(0.2)
            bot.reply_to(message, ai_reply)
        except Exception as e:
            print(f"Ошибка ИИ в группе: {e}")
        return

if __name__ == "__main__":
    bot.remove_webhook()
    print("Бот с OpenRouter запущен!")
    bot.infinity_polling()
    
