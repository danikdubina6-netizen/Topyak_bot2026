import os
import time
import telebot
import requests

TELEGRAM_TOKEN = "8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Безопасно цепляем ключ из секретов GitHub
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY")
BOT_USERNAME = "assistantasil_bot".lower()

def get_openrouter_response(prompt_text):
    if not API_KEY:
        return "Ошибка: API-ключ не найден в секретах GitHub!"
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Topyak Bot",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "Ты крутой, дерзкий и умный помощник. Отвечай интересно, по делу, с вайбом."
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
            err = result.get('error', {}).get('message', 'Неизвестная ошибка')
            return f"Ошибка ответа ИИ: {err}"
    except Exception as e:
        return f"Сбой запроса: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.id == bot.get_me().id:
        return

    chat_type = message.chat.type
    text = message.text.lower() if message.text else ""

    # Личные сообщения — сразу в нейросеть
    if chat_type == 'private':
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_openrouter_response(message.text)
        bot.send_message(message.chat.id, reply)
        return

    # Группы — отвечаем только при упоминании или реплае
    is_mentioned = f"@{BOT_USERNAME}" in text
    is_reply = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id

    if is_mentioned or is_reply:
        bot.send_chat_action(message.chat.id, 'typing')
        clean_prompt = message.text.replace(f"@{BOT_USERNAME}", "").strip()
        reply = get_openrouter_response(clean_prompt if clean_prompt else "Че как?")
        bot.reply_to(message, reply)
        return

if __name__ == "__main__":
    bot.remove_webhook()
    print("Бот с OpenRouter запущен!")
    bot.infinity_polling()
    
