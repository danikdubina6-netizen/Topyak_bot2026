import os
import random
import telebot

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

BOT_USERNAME = ""
try:
    bot_info = bot.get_me()
    BOT_USERNAME = bot_info.username.lower()
except Exception:
    pass

chat_counters = {}

# Список мусорных слов (стоп-слов), которые не несут глубокого смысла для подбора мудрости
STOP_WORDS = {
    что, это, как, все, ее, его, они, мы, вы, мне, тебе, нас, вас, них, 
    для, над, под, при, про, без, из, от, до, по, за, об, обо, или, зато, 
    если, ли, бы, же, то, но, а, и, в, во, к, ко, с, со, о, у, я, ты, он, она, они
}

def find_smart_reply(user_text: str) -> str:
    if not os.path.exists("phrases.txt"):
        return "Файл с базой мудрости (phrases.txt) не найден, но дух Топая силен!"

    with open("phrases.txt", "r", encoding="utf-8") as f:
        phrases = [line.strip() for line in f if line.strip()]
    
    if not phrases:
        return "Молчание — золото, но база фраз пуста."

    if not user_text:
        return random.choice(phrases)

    # Чистим текст, убираем знаки препинания и выделяем только важные слова (исключая стоп-слова и короткие)
    words_raw = user_text.lower().split()
    user_words = {
        w.strip('.,!?;:«»""()-') for w in words_raw 
        if len(w) > 3 and w.strip('.,!?;:«»""()-') not in STOP_WORDS
    }
    
    if not user_words:
        return random.choice(phrases)

    best_phrase = None
    max_matches = 0
    matching_phrases = []

    # Ищем фразы с максимальным количеством совпадений именно смысловых слов
    for phrase in phrases:
        phrase_words = set(w.lower().strip('.,!?;:«»""()-') for w in phrase.split())
        matches = len(user_words.intersection(phrase_words))
        
        if matches > max_matches:
            max_matches = matches
            matching_phrases = [phrase]  найден новый рекорд — сбрасываем список и пишем этот
        elif matches == max_matches and matches > 0:
            matching_phrases.append(phrase)  добавляем в копилку с таким же количеством совпадений

    # Если нашли точечные совпадения, выбираем случайно среди самых релевантных
    if matching_phrases and max_matches > 0:
        return random.choice(matching_phrases)
    else:
        # Если прямых пересечений по смыслу не нашлось, берем случайную мудрость из базы
        return random.choice(phrases)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Здаров! Тоб на связи. Настроен на точечный и глубокий подбор мудрости.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_text = message.text if message.text else ""
    
    is_reply_to_bot = (
        message.reply_to_message 
        and message.reply_to_message.from_user 
        and message.reply_to_message.from_user.id == bot.get_me().id
    )
    
    is_mentioned = BOT_USERNAME and f"@{BOT_USERNAME}" in user_text.lower()

    # Личка, реплай на бота или упоминание — отвечаем мгновенно и точечно
    if message.chat.type == 'private' or is_reply_to_bot or is_mentioned:
        clean_text = user_text.replace(f"@{BOT_USERNAME}", "").strip() if BOT_USERNAME else user_text
        reply_phrase = find_smart_reply(clean_text)
        bot.reply_to(message, reply_phrase)
        return

    # В группах — считаем до 15 сообщений
    chat_counters[chat_id] = chat_counters.get(chat_id, 0) + 1

    if chat_counters[chat_id] >= 15:
        chat_counters[chat_id] = 0
        reply_phrase = find_smart_reply(user_text)
        bot.reply_to(message, reply_phrase)

if __name__ == "__main__":
    print("Бот Топяский Философ и Мудрец запущен в режиме повышенной точности...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
