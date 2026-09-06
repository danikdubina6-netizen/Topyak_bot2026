import os
import random
import threading
import time
import telebot
from flask import Flask

TELEGRAM_TOKEN = os.environ.get(
    "TOKEN", "8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4"
)
BOT_USERNAME = "@Assistantasil_bot"

bot_status = "Инициализация..."
bot = None
BOT_ID = None

try:
  bot = telebot.TeleBot(TELEGRAM_TOKEN)
  BOT_ID = int(TELEGRAM_TOKEN.split(":")[0])
  bot_status = "Бот успешно создан!"
except Exception as e:
  bot_status = f"Ошибка создания бота: {e}"

PHRASES = [
    "Сам ты {text}, кожаный мешок. 🤖",
    "Чё шумишь, кожаный?",
    "Интересное мнение, но я бы на твоем месте промолчал.",
    "Базар фильтруй, братан.",
    "Жиза.",
    "Кринж.",
    "База.",
    "Тимохуй пидорас.",
    "У Тимофея мать шлюха.",
]


def get_local_response(text):
  text_lower = text.lower()
  if "привет" in text_lower or "ку" in text_lower:
    return "Здарова! Чё как по мастям?"
  elif "топяк" in text_lower:
    return "Великий лидер и создатель на месте."
  chosen = random.choice(PHRASES)
  if "{text}" in chosen:
    return chosen.format(text=text)
  return chosen


if bot:

  @bot.message_handler(commands=["start"])
  def send_welcome(message):
    bot.reply_to(
        message,
        "Готовьтесь пообщаться с Топякским ботом и развлекайтесь рандомно!)",
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

    if is_private or is_reply_to_bot or is_mentioned:
      bot.reply_to(message, get_local_response(text))


def run_bot():
  global bot_status
  try:
    bot.remove_webhook()
    bot_status = "Вебхук сброшен, запущен polling..."
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
  except Exception as e:
    bot_status = f"КРИТИЧЕСКАЯ ОШИБКА ПОЛЛИНГА: {e}"
    print(bot_status)


app = Flask(__name__)


@app.route("/")
def home():
  # Теперь сайт покажет нам точный статус бота прямо в браузере!
  return f"Topyak Bot Status: <b>{bot_status}</b>"


if __name__ == "__main__":
  if bot:
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()

  port = int(os.environ.get("PORT", 8000))
  app.run(host="0.0.0.0", port=port)
  
