import random
import time
import telebot

TELEGRAM_TOKEN = "8888128306:AAFSAMfg3rlLEYRIBZyN2OoJHA26ATyq35s"
BOT_USERNAME = "@Assistantasil_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
BOT_ID = int(TELEGRAM_TOKEN.split(":")[0])

# Полная база фраз (вайбы, философия и троллинг)
PHRASES = [
    "Сам ты {text}, кожаный мешок. 🤖",
    "Чё шумишь, кожаный?",
    "Интересное мнение, но я бы на твоем месте промолчал.",
    "Ага, щас, разбежался.",
    "Базар фильтруй, братан.",
    "Понял-принял, но это не точно.",
    "Информативно. Продолжай наблюдение.",
    "Красиво сказано, аж слеза прошибла.",
    "Ты это серьезно сейчас высрал?",
    "Ну тут без комментариев.",
    "Великолепно! Почти как код на Pydroid без ошибок.",
    "Абонент недоступен, потому что ему лень слушать этот бред.",
    "Лень отвечать, давай по новой.",
    "Чё ты докопался?",
    "Жиза.",
    "Кринж.",
    "База.",
    "Абсолютный фейл.",
    "Работай, братан, не отвлекайся.",
    "Одобряю эту тему.",
    "Сильный ход.",
    "Слабый байт.",
    "По фактам.",
    "Где пруфы, Билли?",
    "Время — деньги, а ты его тратишь на меня.",
    "Забей.",
    "Не парься, дядя.",
    "Ну такое.",
    "Спорно.",
    "Лол, кек, чебурек.",
    "Я бот локальный, мне похуй глобально.",
    "Просто пиздец.",
    "Какая боль.",
    "Атмосферно.",
    "Ну вы даете, конечно.",
    "А ты хорош.",
    "Похуй, пляшем.",
    "Держи в курсе.",
    "Не благодари.",
    "Я не понял, но очень интересно.",
    "Всё гениальное — просто, а ты — нет.",
    "Гениально, как код с while true.",
    "Мне кажется, ты пиздишь.",
    "Это успех.",
    "Найс трай.",
    "Да ладно?",
    "Ой, всё.",
    "Серьезно?",
    "В голос.",
    "Ну бывает.",
    "Дай подумать... Нет.",
    "И чё?",
    "Сочувствую.",
    "Иди нахуй, пожалуйста.",
    "Без обид, но ты не прав.",
    "Ты меня пугаешь.",
    "Не сегодня.",
    "Коротко и ясно.",
    "Слишком сложно, упрости.",
    "Игнорирую твой высер.",
    "Ясно, понятно.",
    "А ты умнее, чем кажешься.",
    "Хуета.",
    "Топчик.",
    # Троллинг
    "Тимохуй пидорас.",
    "У Тимофея мать шлюха.",
    "Сам ты Тимоха.",
    "Тимоха, съебал нахуй.",
    "Тимоха, базару нет.",
    "Тимоха — бот.",
    "А что Тимоха скажет по этому поводу?",
    "Тимоха, отдохни.",
    "Не беси Тимоху.",
    "Тимоха, ты дурак?",
    "Тимоха, тебя не спрашивали.",
    "Тимоха вышел из чата, зашел в очко.",
]


def get_local_response(text):
  text_lower = text.lower()

  # Попугай ("Скажи...")
  if text_lower.startswith("скажи"):
    to_repeat = text[5:].strip()
    if to_repeat:
      return to_repeat
    return "Скажи что?"

  # Триггеры
  if "привет" in text_lower or "ку" in text_lower:
    return "Здарова! Чё как по мастям?"
  elif "как дела" in text_lower:
    return "Всё пучком, Pydroid тащит."
  elif "ты кто" in text_lower:
    return "Я локальный бот Топяка, работаю на чистых вайбах."
  elif "пока" in text_lower:
    return "Давай, на связи!"
  elif "топяк" in text_lower:
    return "Великий лидер и создатель на месте."

  # Рандом из базы
  chosen = random.choice(PHRASES)
  if "{text}" in chosen:
    return chosen.format(text=text)
  return chosen


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(message, f"Ку! Загрузил базу из {len(PHRASES)} фраз, погнали.")


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
  text = message.text or ""
  is_reply_to_bot = (
      message.reply_to_message
      and message.reply_to_message.from_user.id == BOT_ID
  )
  is_mentioned = BOT_USERNAME.lower() in text.lower()

  # Бот отвечает на реплай или на упоминание юзернейма
  if is_reply_to_bot or is_mentioned:
    reply_text = get_local_response(text)
    bot.reply_to(message, reply_text)


print(f"Бот запущен! База: {len(PHRASES)} фраз. Ждет реплаев и упоминаний...")

# Защита от обрывов связи
while True:
  try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
  except Exception as e:
    print(f"Переподключение: {e}")
    time.sleep(3)
