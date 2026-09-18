import os
import random
import telebot

# Получаем токен из секретов GitHub Actions
TOKEN = os.getenv('TOKEN')
if not TOKEN:
  raise ValueError('Не найден токен! Проверь настройки GitHub Secrets (TOKEN).')

bot = telebot.TeleBot(TOKEN)

# Счётчик сообщений для групп/супергрупп
group_message_counter = 0


# Функция для загрузки фраз из внешнего файла
def load_phrases(filename='phrases.txt'):
  if not os.path.exists(filename):
    # Запасной вариант, если файла вдруг нет
    return [
        'Жизнь измеряется не количеством вдохов, а моментами, когда от счастья захватывает дух.',
        'Сентябрь 2026: время новых трендов и крутых мемов.',
    ]

  with open(filename, 'r', encoding='utf-8') as f:
    # Читаем строки, убираем пустые и лишние пробелы по краям
    phrases = [line.strip() for line in f if line.strip()]

  print(f'Загружено фраз из файла: {len(phrases)}')
  return phrases


# Загружаем базу при старте
RANDOM_PHRASES = load_phrases()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      (
          f'Привет! Я бот проекта Топяк. В моей внешней базе загружено'
          f' {len(RANDOM_PHRASES)} фраз. Напиши мне что-нибудь.'
      ),
  )


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
  global group_message_counter

  chat_type = message.chat.type
  text = message.text or ''
  text_lower = text.lower()

  # 1. ПРИОРИТЕТ: Фича "Скажи..."
  if text_lower.startswith('скажи '):
    said_text = text[6:].strip()
    if said_text:
      bot.reply_to(message, said_text)
      return

  # 2. Личные сообщения
  if chat_type == 'private':
    response_text = random.choice(RANDOM_PHRASES)
    bot.reply_to(message, response_text)
    return

  # 3. Группы и супергруппы
  if chat_type in ['group', 'supergroup']:
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user.id == bot.get_me().id
    )
    is_mentioned = False

    bot_username = bot.get_me().username
    if bot_username and f'@{bot_username.lower()}' in text_lower:
      is_mentioned = True

    if is_reply_to_bot or is_mentioned:
      response_text = random.choice(RANDOM_PHRASES)
      bot.reply_to(message, response_text)
      return

    # Фоновые сообщения в группе — считаем до 15
    group_message_counter += 1
    if group_message_counter >= 15:
      group_message_counter = 0

      action_type = random.choice(['reply', 'reaction'])
      if action_type == 'reply':
        response_text = random.choice(RANDOM_PHRASES)
        bot.reply_to(message, response_text)
      else:
        try:
          bot.set_message_reaction(
              message.chat.id,
              message.message_id,
              [telebot.types.ReactionTypeEmoji('🔥')],
          )
        except Exception:
          response_text = random.choice(RANDOM_PHRASES)
          bot.reply_to(message, response_text)


if __name__ == '__main__':
  print('Бот с внешним файлом фраз запущен...')
  try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
  except Exception as e:
    print(f'Сессия завершена: {e}')
      
