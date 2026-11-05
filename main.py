import os
import random
import telebot

# Получаем токен из переменных окружения (или можно вставить строкой, но через env безопаснее)
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    # Если токен передается через секреты GitHub Actions / окружение
    pass

bot = telebot.TeleBot(TOKEN)

# Функция для поиска подходящей фразы из файла phrases.txt
def find_smart_reply(user_text: str) -> str:
    # Проверяем, существует ли файл с базой
    if not os.path.exists("phrases.txt"):
        return "Файл с базой мудрости (phrases.txt) не найден, но дух Топая силен!"

    # Загружаем все фразы из файла
    with open("phrases.txt", "r", encoding="utf-8") as f:
        phrases = [line.strip() for line in f if line.strip()]
    
    if not phrases:
        return "Молчание — золото, но база фраз пуста."

    # Если текста сообщения нет (например, картинка или стикер), берем рандомную мудрость
    if not user_text:
        return random.choice(phrases)

    # Чистим текст пользователя и разбиваем на слова (исключая короткие слова < 4 символов)
    user_words = set(w.lower() for w in user_text.split() if len(w) > 3)
    
    if not user_words:
        return random.choice(phrases)

    best_phrase = None
    max_matches = 0

    # Ищем фразу, в которой больше всего пересекающихся ключевых слов с сообщением
    for phrase in phrases:
        phrase_words = set(w.lower() for w in phrase.split())
        matches = len(user_words.intersection(phrase_words))
        
        if matches > max_matches:
            max_matches = matches
            best_phrase = phrase

    # Если нашли точечное совпадение — возвращаем его, если совпадений 0 — берем рандом
    if best_phrase and max_matches > 0:
        return best_phrase
    else:
        return random.choice(phrases)

# Обработчик команды /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Здаров! Тоб на связи. Задавай вопрос или пиши мысли — выдам базу.")

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Получаем текст сообщения пользователя
    user_text = message.text if message.text else ""
    
    # Ищем умную мудрость под контекст
    reply_phrase = find_smart_reply(user_text)
    
    # Отправляем ответ реплаем на сообщение пользователя
    bot.reply_to(message, reply_phrase)

if __name__ == "__main__":
    print("Бот Топякский Мудрец запущен и готов раздавать мудрость...")
    # Запуск поллинга с автопереподключением при сбоях сети
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
  
