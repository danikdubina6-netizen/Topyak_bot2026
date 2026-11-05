import os
import random
import telebot

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Словарь для подсчета сообщений отдельно в каждой группе/чате
chat_counters = {}

def find_smart_reply(user_text: str) -> str:
    if not os.path.exists("phrases.txt"):
        return "Файл с базой мудрости (phrases.txt) не найден, но дух Топая силен!"

    with open("phrases.txt", "r", encoding="utf-8") as f:
        phrases = [line.strip() for line in f if line.strip()]
    
    if not phrases:
        return "Молчание — золото, но база фраз пуста."

    if not user_text:
        return random.choice(phrases)

    # Выделяем ключевые слова (длиннее 3 символов)
    user_words = set(w.lower() for w in user_text.split() if len(w) > 3)
    
    if not user_words:
        return random.choice(phrases)

    best_phrase = None
    max_matches = 0

    # Сравниваем слова пользователя со словами из баз фраз
    for phrase in phrases:
        phrase_words = set(w.lower() for w in phrase.split())
        matches = len(user_words.intersection(phrase_words))
        
        if matches > max_matches:
            max_matches = matches
            best_phrase = phrase

    if best_phrase and max_matches > 0:
        return best_phrase
    else:
        return random.choice(phrases)

# Обработчик команд (на них ответит сразу)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Здаров! Тоб на связи. Считаю 15 сообщений и выдаю точечную базу.")

# Обработчик всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id

    # В личке с ботом отвечает на каждое сообщение
    if message.chat.type == 'private':
        user_text = message.text if message.text else ""
        reply_phrase = find_smart_reply(user_text)
        bot.reply_to(message, reply_phrase)
        return

    # Логика для групп: считаем сообщения для каждого чата отдельно
    chat_counters[chat_id] = chat_counters.get(chat_id, 0) + 1

    # Как только набралось 15 сообщений — выдаем ответ
    if chat_counters[chat_id] >= 15:
        chat_counters[chat_id] = 0  # Сбрасываем счетчик
        
        user_text = message.text if message.text else ""
        reply_phrase = find_smart_reply(user_text)
        
        # Отвечаем реплаем на 15-е сообщение
        bot.reply_to(message, reply_phrase)

if __name__ == "__main__":
    print("Бот Топякский Философ запущен (режим: 1 ответ на 15 сообщений в группах)...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    
