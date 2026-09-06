import os
import random
import telebot

# Токен берется из секретов GitHub Actions
TELEGRAM_TOKEN = os.environ.get("TOKEN")
BOT_USERNAME = "@Assistantasil_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
BOT_ID = int(TELEGRAM_TOKEN.split(":")[0])

# Умные триггеры: связки ключевых слов и вариантов ответов
SMART_TRIGGERS = {
    ("привет", "ку", "здарова", "хай", "салют"): [
        "Здарова! На связи цифровая база.",
        "Привет-привет, кожаный. Чё как по мастям?",
        "О, здарова. Какими судьбами в моём терминале?",
    ],
    ("топяк", "создатель", "автор", "кто тебя сделал"): [
        "Мой создатель — Топяк. Легенда цифрового мира.",
        "Меня написала правильная команда под руководством Топяка.",
        "Создатель этого бота — Топяк, гений разработки.",
    ],
    ("код", "питон", "python", "github", "скрипт"): [
        "Код чистый, как слеза программиста. GitHub Actions держит 24/7!",
        "Пишу на Python, кручусь в облаке GitHub. Всё по красоте.",
        "Мой код — это искусство. Никаких лишних отступов!",
    ],
    ("музыка", "цой", "рок", "песня"): [
        "Группа КИНО и Виктор Цой — это вечная база.",
        "Музыка — моё всё. Особенно если с хорошим битом.",
        "Включаю режим 1980-х: перемен требуют наши сердца!",
    ],
    ("как дела", "чё каво", "что нового"): [
        "Всё стабильно, процессоры греются, код пашет.",
        "Живу в облаке, обрабатываю твои сообщения. Полный кайф.",
    ],
}

PHRASES = [
    "Сам ты {text}, кожаный мешок. 🤖",
    "Чё шумишь, кожаный?",
    "Интересное мнение, но я бы на твоем месте промолчал.",
    "Базар фильтруй, братан.",
    "Жиза.",
    "Кринж.",
    "База.",
    "По фактам разъебал, но всем пофиг.",
    "И чё ты мне сделаешь? Я в облаке живу.",
    "Слишком умно для меня, давай проще.",
    "Ошибка 404: уважение к собеседнику не найдено.",
    "Гениально, но нет.",
    "Иди уроки учи, программист комнатный.",
    "Ну ты и душноту нагнал...",
    "Ладно, уговорил, звучит хайпово.",
    "Это мы одобряем. 👍",
    "Нормально делай — нормально будет.",
    "Имба лютая.",
    "Это база, остальное — лирика.",
    "Мои нейросети плавятся от твоих гениальных мыслей.",
]


def get_local_response(text):
    text_lower = text.lower().strip()

    if text_lower.startswith("скажи "):
        return text[6:].strip() or "Чего сказать-то?"

    for keywords, responses in SMART_TRIGGERS.items():
        if any(keyword in text_lower for keyword in keywords):
            return random.choice(responses)

    chosen = random.choice(PHRASES)
    if "{text}" in chosen:
        return chosen.format(text=text)
    return chosen


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Бот переведен на проверенную систему ответов. Полёт нормальный! 😎",
    )


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.from_user.id == BOT_ID:
        return

    text = message.text or ""
    is_private = message.chat.type == "private"
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == BOT_ID
    )
    is_mentioned = BOT_USERNAME.lower() in text.lower()
    is_random_burst = (not is_private) and (random.random() < 0.15)

    if is_private or is_reply_to_bot or is_mentioned or is_random_burst:
        bot.reply_to(message, get_local_response(text))


if __name__ == "__main__":
    print("Запуск бота через GitHub Actions...")
    bot.remove_webhook()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
