import os
import random
import time
import telebot
from flask import Flask

TELEGRAM_TOKEN = os.environ.get("TOKEN")
BOT_USERNAME = "@Assistantasil_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
BOT_ID = int(TELEGRAM_TOKEN.split(":")[0]) if TELEGRAM_TOKEN else 0

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
  if text_lower.startswith("скажи"):
    to_repeat = text[5:].strip()
    if to_repeat:
      return to_repeat
    return "Скажи что?"

  if "привет" in text_lower or "ку" in text_lower:
    return "Здарова! Чё как по мастям?"
  elif "как дела" in text_lower:
    return "Всё пучком, облака тащат."
  elif "ты кто" in text_lower:
    return "Я облачный бот Топяка, работаю на чистых вайбах."
  elif "пока" in text_lower:
    return "Давай, на связи!"
  elif "топяк" in text_lower:
    return "Великий лидер и создатель на месте."

  chosen = random.choice(PHRASES)
  if "{text}" in chosen:
    return chosen.format(text=text)
  return chosen


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(message, f"Ку! Я в облаке. База: {len(PHRASES)} фраз.")


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
  text = message.text or ""
  is_reply_to_message = message.reply_to_message
  is_reply_to_bot = (
      is_reply_to_message
      and is_reply_to_message.from_user
      and is_reply_to_message.from_user.id == BOT_ID
  )
  is_mentioned = BOT_USERNAME.lower() in text.lower()

  if is_reply_to_bot or is_mentioned:
    reply_text = get_local_response(text)
    bot.reply_to(message, reply_text)


# Создаем Flask-приложение, которое сразу открывает порт для Render
app = Flask(__name__)


@app.route("/")
def home():
  return "Topyak Bot is alive!"


def run_bot():
  while True:
    try:
      bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
      print(f"Переподключение: {e}")
      time.sleep(3)


# Запускаем бота в фоновом потоке сразу при старте файла
import threading

t = threading.Thread(target=run_bot, daemon=True)
t.start()
