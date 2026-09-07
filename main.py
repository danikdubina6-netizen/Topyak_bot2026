import os
import random
import telebot
from telebot import types

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Хранилище состояний пользователей (в памяти бота)
# Ключ: chat_id, Значение: режим ('own', 'echo', 'mix')
user_modes = {}

# (Вся огромная база фраз остается здесь же)
GREETINGS = [
    "О, живой человек в терминале. Говори, чё хотел.",
    "Здорово, программист. Какую фичу сегодня ломаем?",
    "Привет. Опять ты со своими гениальными идеями."
]

SMART_RESPONSES = [
    "Интересный тейк, но давай ближе к делу, кожаный.",
    "Не душни, давай по фактам или никак.",
    "Загрузил процессор своими мыслями. Пойду остыну."
]

TOXIC_ROASTS = [
    "Ошибка 404: уважение к собеседнику не найдено.",
    "Кринг.",
    "Бот написан на коленке, но работает стабильнее твоей личной жизни."
]

TECH_QUOTES = [
    "Работает — не трогай. Золотое правило системного администратора.",
    "Костыли — это фундамент любого великого проекта."
]

VIBE_QUOTES = [
    "Синтезаторы, драм-машины и холодный свет монитора — вот это вайб.",
    "Жизнь — это трек в КапКуте: обрезал лишнее, наложил фильтр, погнали дальше."
]

ALL_PHRASES = GREETINGS + SMART_RESPONSES + TOXIC_ROASTS + TECH_QUOTES + VIBE_QUOTES

# Главное меню с кнопками выбора режима
def get_settings_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🗣 Только свои фразы", callback_data="mode_own"),
        types.InlineKeyboardButton("🔄 Повторять за мной", callback_data="mode_echo"),
        types.InlineKeyboardButton("🔀 Микс (свои + повтор)", callback_data="mode_mix")
    )
    return markup

@bot.message_handler(commands=['start', 'help', 'mode'])
def send_welcome(message):
    chat_id = message.chat.id
    # Устанавливаем режим по умолчанию, если его еще не было
    if chat_id not in user_modes:
        user_modes[chat_id] = 'own'
        
    current_mode = user_modes[chat_id]
    mode_names = {
        'own': '🗣 Только свои фразы',
        'echo': '🔄 Повторять за мной',
        'mix': '🔀 Микс (свои + повтор)'
    }
    
    welcome_text = (
        f"🤖 **Топякский ИИ** на связи.\n"
        f"Текущий режим: *{mode_names.get(current_mode)}*\n\n"
        f"Выбирай режим работы ниже:"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_settings_keyboard(), parse_mode='Markdown')

# Обработка нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_mode_callback(call):
    chat_id = call.message.chat.id
    new_mode = call.data.split('_')[1]
    user_modes[chat_id] = new_mode
    
    mode_titles = {
        'own': '🗣 Только свои фразы',
        'echo': '🔄 Повторять за мной',
        'mix': '🔀 Микс (свои + повтор)'
    }
    
    bot.answer_callback_query(call.id, f"Режим изменен!")
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🤖 Режим успешно переключен!\nТекущий режим: *{mode_titles.get(new_mode)}*",
        reply_markup=get_settings_keyboard(),
        parse_mode='Markdown'
    )

# Обработчик всех текстовых сообщений с учетом выбранного режима
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    # Если режим не задан, ставим 'own' по умолчанию
    mode = user_modes.get(chat_id, 'own')
    
    text_lower = message.text.lower()
    
    # Логика генерации ответа в зависимости от режима
    if mode == 'echo':
        # Режим «Повторять за мной»
        response = message.text
        
    elif mode == 'own':
        # Режим «Только свои фразы» (с умными триггерами)
        if any(word in text_lower for word in ['привет', 'здарова', 'ку', 'здаров', 'хай']):
            response = random.choice(GREETINGS)
        elif any(word in text_lower for word in ['код', 'питон', 'скрипт', 'ошибка', 'баг', 'сервер']):
            response = random.choice(TECH_QUOTES)
        elif any(word in text_lower for word in ['музыка', 'трек', 'вайб', 'космос', 'жизнь']):
            response = random.choice(VIBE_QUOTES)
        elif any(word in text_lower for word in ['дурак', 'тупой', 'кринж', 'бот']):
            response = random.choice(TOXIC_ROASTS)
        else:
            response = random.choice(ALL_PHRASES)
            
    elif mode == 'mix':
        # Режим «Микс»: 50% шанс выдать свою фразу или повторить твою
        if random.choice([True, False]):
            response = message.text
        else:
            if any(word in text_lower for word in ['привет', 'здарова', 'ку', 'хай']):
                response = random.choice(GREETINGS)
            else:
                response = random.choice(ALL_PHRASES)
    else:
        response = message.text

    bot.reply_to(message, response)

if __name__ == '__main__':
    print("Бот запущен и готов к работе...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    
