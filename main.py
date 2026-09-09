import os
import random
import telebot
from openai import OpenAI

# Прямо прописанные ключи для запуска
TELEGRAM_TOKEN = "8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4"
NEBIUS_API_KEY = "project-u00wrw8mkc00e3bz83x47h"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Инициализация клиента Nebius AI
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=NEBIUS_API_KEY
)

AVAILABLE_REACTIONS = [
    "👍", "🔥", "❤️", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
    "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱"
]

COUNTER_FILE = "counter.txt"

def get_current_count():
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0
    return 0

def save_current_count(count):
    try:
        with open(COUNTER_FILE, "w") as f:
            f.write(str(count))
    except Exception:
        pass

def get_nebius_reply(user_text):
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — Топякский ИИ, дерзкий, умный и крутой ассистент разработчика. Отвечай кратко, с вайбом, без лишней воды и душноты."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Оу, ошибка нейронки: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Игнорируем самого себя, чтобы избежать циклов
    if message.from_user.is_bot:
        return

    text = message.text or ""

    # Фильтр спам-рекламы
    spam_words = ["пробив", "госномер", "поиск человека", "бесплатно", "vpn", "впн"]
    if any(word in text.lower() for word in spam_words):
        try:
            bot.delete_message(message.chat.id, message.id)
        except Exception:
            pass
        return

    # Считаем сообщения
    count = get_current_count() + 1
    save_current_count(count)
    
    print(f"Сообщение #{count} в чате {message.chat.id}")

    # Отвечаем ровно на каждое 15-е сообщение
    if count % 15 == 0:
        reply_text = get_nebius_reply(text)
        sent_msg = bot.reply_to(message, reply_text)

        try:
            reaction = random.choice(AVAILABLE_REACTIONS)
            bot.set_message_reaction(
                message.chat.id,
                sent_msg.message_id,
                [telebot.types.ReactionTypeEmoji(reaction)]
            )
        except Exception:
            pass

if __name__ == "__main__":
    print("Бот со вшитыми токенами запущен...")
    bot.infinity_polling()
    
