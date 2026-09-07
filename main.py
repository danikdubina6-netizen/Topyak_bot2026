import os
import random
import telebot
from telebot import types

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Хранилища состояний и памяти пользователей
user_modes = {}      # Режимы работы для чатов
user_history = {}    # Память: история фраз, сказанных пользователем в этом чате

# База фраз
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
        types.InlineKeyboardButton("🔀 И то и то (Микс + Память)", callback_data="mode_mix")
    )
    return markup

@bot.message_handler(commands=['start', 'help', 'mode'])
def send_welcome(message):
    chat_id = message.chat.id
    current_mode = user_modes.get(chat_id, 'own')
    
    mode_names = {
        'own': '🗣 Говорить свои фразы',
        'echo': '🔄 Повторять чужие фразы',
        'mix': '🔀 И то и то (Микс + Память)'
    }
    
    welcome_text = (
        f"🤖 **Топякский ИИ** на связи.\n"
        f"Текущий режим: *{mode_names.get(current_mode, 'Свои фразы')}*\n\n"
        f"🧠 Память чата активирована: я запоминаю твои фразы и могу отвечать ими из архива!\n\n"
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
        'mix': '🔀 И то и то (Микс + Память)'
    }
    
    bot.answer_callback_query(call.id, "Режим успешно изменен!")
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"✅ **Режим зафиксирован:**\n*{mode_titles.get(new_mode)}*\n\nМожешь писать сообщения в чат!",
        reply_markup=get_settings_keyboard(),
        parse_mode='Markdown'
    )

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text
    
    # 1. Инициализируем режим по умолчанию, если нет
    if chat_id not in user_modes:
        user_modes[chat_id] = 'own'

    # 2. Сохраняем фразу пользователя в память чата (историю)
    if chat_id not in user_history:
        user_history[chat_id] = []
    
    # Добавляем фразу, если её нет в истории (чтобы не было дубликатов подряд)
    if text not in user_history[chat_id]:
        user_history[chat_id].append(text)
        # Ограничим память последними 100 фразами, чтобы не перегружать память
        if len(user_history[chat_id]) > 100:
            user_history[chat_id].pop(0)

    mode = user_modes[chat_id]
    text_lower = text.lower()
    
    # 3. Логика генерации ответа
    if mode == 'echo':
        # Чистое эхо — всегда повторяет текущее сообщение
        response = text
        
    elif mode == 'own':
        # Свои фразы + иногда может вспомнить старую фразу из истории (если она там есть)
        if user_history[chat_id] and len(user_history[chat_id]) > 3 and random.random() < 0.25:
            # 25% шанс вытащить что-то из архива памяти
            response = random.choice(user_history[chat_id])
        else:
            # Обычные умные ответы
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
        # Режим Микс: выбирает либо текущее сообщение, либо рандомную фразу из базы, либо фразу из истории памяти чата
        choice_pool = ['current', 'base']
        if user_history[chat_id]:
            choice_pool.append('history')
            
        selected_source = random.choice(choice_pool)
        
        if selected_source == 'current':
            response = text
        elif selected_source == 'history':
            response = random.choice(user_history[chat_id])
        else:
            response = random.choice(ALL_PHRASES)
    else:
        response = random.choice(ALL_PHRASES)

    bot.reply_to(message, response)

if __name__ == '__main__':
    print("Бот запущен и готов к работе...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
                                                     
