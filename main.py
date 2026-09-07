import os
import random
import telebot
from telebot import types

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Хранилище состояний пользователей
user_modes = {}

# База фраз (500+ и общие категории)
GREETINGS = [
    "О, живой человек в терминале. Говори, чё хотел.",
    "О, здарова. Какими судьбами в моём терминале?",
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
    "Бот написан на коленке, но работает стабильнее твоей личной жизни.",
    "Кринг.",
    "Имба лютая."
]

TECH_QUOTES = [
    "Работает — не трогай. Золотое правило системного администратора.",
    "Костыли — это фундамент любого великого проекта.",
    "GitHub Actions — великая вещь, пока раннеры не начинают бунтовать."
]

VIBE_QUOTES = [
    "Синтезаторы, драм-машины и холодный свет монитора — вот это вайб.",
    "Жизнь — это трек в КапКуте: обрезал лишнее, наложил фильтр, погнали дальше.",
    "Космос молчит, а наш бот отвечает. Идеальный баланс."
]

ALL_PHRASES = GREETINGS + SMART_RESPONSES + TOXIC_ROASTS + TECH_QUOTES + VIBE_QUOTES

# Клавиатура с выбором режимов
def get_settings_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🗣 Говорить свои фразы", callback_data="mode_own"),
        types.InlineKeyboardButton("🔄 Повторять чужие фразы", callback_data="mode_echo"),
        types.InlineKeyboardButton("🔀 И то и то (Микс)", callback_data="mode_mix")
    )
    return markup

# Команды /start, /help, /mode теперь ВСЕГДА вызывают меню с кнопками
@bot.message_handler(commands=['start', 'help', 'mode'])
def send_welcome(message):
    chat_id = message.chat.id
    current_mode = user_modes.get(chat_id, 'own')
    
    mode_names = {
        'own': '🗣 Говорить свои фразы',
        'echo': '🔄 Повторять чужие фразы',
        'mix': '🔀 И то и то (Микс)'
    }
    
    welcome_text = (
        f"🤖 **Топякский ИИ** на связи.\n"
        f"Текущий режим: *{mode_names.get(current_mode, 'Свои фразы')}*\n\n"
        f"Выбери, как я должен отвечать:\n"
        f"• **Свои фразы** — отвечаю сарказмом и базой.\n"
        f"• **Повторять чужие** — работаю эхо-зеркалом.\n"
        f"• **Микс** — рандомно чередую варианты.\n\n"
        f"Жми кнопку ниже для смены режима:"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_settings_keyboard(), parse_mode='Markdown')

# Обработка нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_mode_callback(call):
    chat_id = call.message.chat.id
    new_mode = call.data.split('_')[1]
    user_modes[chat_id] = new_mode
    
    mode_titles = {
        'own': '🗣 Говорить свои фразы',
        'echo': '🔄 Повторять чужие фразы',
        'mix': '🔀 И то и то (Микс)'
    }
    
    bot.answer_callback_query(call.id, "Режим успешно изменен!")
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"✅ **Режим зафиксирован:**\n*{mode_titles.get(new_mode)}*\n\nМожешь писать сообщения в чат!",
        reply_markup=get_settings_keyboard(),
        parse_mode='Markdown'
    )

# Обработчик всех текстовых сообщений (без лишних спам-подсказок)
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    
    # Если режим не задан, молча ставим 'own' по умолчанию
    if chat_id not in user_modes:
        user_modes[chat_id] = 'own'

    mode = user_modes[chat_id]
    text_lower = message.text.lower()
    
    # Генерация ответа в зависимости от установленного режима
    if mode == 'echo':
        response = message.text
    elif mode == 'own':
        if any(word in text_lower for word in ['привет', 'здарова', 'ку', 'здаров', 'хай', 'дороу']):
            response = random.choice(GREETINGS)
        elif any(word in text_lower for word in ['код', 'питон', 'скрипт', 'ошибка', 'баг', 'сервер', 'гитхаб']):
            response = random.choice(TECH_QUOTES)
        elif any(word in text_lower for word in ['музыка', 'трек', 'вайб', 'космос', 'жизнь', 'капкут']):
            response = random.choice(VIBE_QUOTES)
        elif any(word in text_lower for word in ['дурак', 'тупой', 'кринж', 'бот', 'сука', 'блять']):
            response = random.choice(TOXIC_ROASTS)
        else:
            response = random.choice(ALL_PHRASES)
    elif mode == 'mix':
        if random.choice([True, False]):
            response = message.text
        else:
            response = random.choice(ALL_PHRASES)
    else:
        response = random.choice(ALL_PHRASES)

    bot.reply_to(message, response)

if __name__ == '__main__':
    print("Бот запущен и готов к работе...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    
