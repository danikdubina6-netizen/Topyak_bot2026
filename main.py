import os
import random
import telebot
from telebot import types

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Получаем ID самого бота при старте, чтобы исключить его из самоответов
BOT_ID = None
try:
    BOT_ID = bot.get_me().id
except Exception:
    pass

# Хранилища состояний, памяти и счетчиков для групп
user_modes = {}       # Режимы работы (own, echo, mix) для чатов
user_history = {}     # Память: история фраз
group_toggles = {}    # Разрешено ли боту болтать в группе (True/False)
message_counters = {} # Счетчик сообщений для лимита в 15 штук в группах

# База фраз бота
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

ALL_BASE_PHRASES = GREETINGS + SMART_RESPONSES + TOXIC_ROASTS + TECH_QUOTES + VIBE_QUOTES

# Клавиатура с выбором режимов
def get_settings_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🗣 Говорить свои фразы (база бота)", callback_data="mode_own"),
        types.InlineKeyboardButton("🔄 Повторять чужие фразы (из истории)", callback_data="mode_echo"),
        types.InlineKeyboardButton("🔀 И то и то (Микс вариантов)", callback_data="mode_mix")
    )
    
    # Кнопка включения/выключения бота в группе
    is_active = group_toggles.get(chat_id, True)
    toggle_text = "🔕 Выключить бота в этой группе" if is_active else "🔔 Включить бота в этой группе"
    markup.add(types.InlineKeyboardButton(toggle_text, callback_data="toggle_group"))
    return markup

@bot.message_handler(commands=['start', 'help', 'mode', 'toggle'])
def send_welcome(message):
    chat_id = message.chat.id
    current_mode = user_modes.get(chat_id, 'own')
    
    mode_names = {
        'own': '🗣 Говорить свои фразы',
        'echo': '🔄 Повторять чужие фразы (из истории)',
        'mix': '🔀 И то и то (Микс)'
    }
    
    welcome_text = (
        f"🤖 **Топякский ИИ** на связи.\n"
        f"Текущий режим: *{mode_names.get(current_mode, 'Свои фразы')}*\n"
        f"Статус в чате: *{'Активен' if group_toggles.get(chat_id, True) else 'Молчит'}*\n\n"
        f"Настрой бота кнопками ниже:"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_settings_keyboard(chat_id), parse_mode='Markdown')

# Обработка нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if data.startswith('mode_'):
        new_mode = data.split('_')[1]
        user_modes[chat_id] = new_mode
        bot.answer_callback_query(call.id, "Режим успешно изменен!")
        
        mode_titles = {
            'own': '🗣 Говорить свои фразы',
            'echo': '🔄 Повторять чужие фразы (из истории)',
            'mix': '🔀 И то и то (Микс)'
        }
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"✅ **Режим обновлен:**\n*{mode_titles.get(new_mode)}*\n\nНастройки чата:",
            reply_markup=get_settings_keyboard(chat_id),
            parse_mode='Markdown'
        )
        
    elif data == 'toggle_group':
        current_state = group_toggles.get(chat_id, True)
        group_toggles[chat_id] = not current_state
        status_str = "включен" if group_toggles[chat_id] else "выключен"
        bot.answer_callback_query(call.id, f"Бот теперь {status_str} в этом чате!")
        
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_settings_keyboard(chat_id)
        )

# Обработчик всех текстовых сообщений (люди + другие боты)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_messages(message):
    global BOT_ID
    if not BOT_ID:
        try:
            BOT_ID = bot.get_me().id
        except Exception:
            pass

    # СТОП-КРАН: Если сообщение отправил сам этот бот — игнорируем, чтобы не было зацикливания
    if BOT_ID and message.from_user.id == BOT_ID:
        return

    chat_id = message.chat.id
    text = message.text
    if not text:
        return

    # 1. Проверяем, разрешено ли боту вообще говорить в этом чате
    if chat_id not in group_toggles:
        group_toggles[chat_id] = True
        
    if not group_toggles[chat_id]:
        return

    # 2. Проверяем легендарную команду "Скажи <текст>"
    if text.lower().startswith('скажи '):
        phrase_to_say = text[6:].strip()
        if phrase_to_say:
            bot.reply_to(message, phrase_to_say)
        return

    # Определяем, групповой ли это чат
    is_group = message.chat.type in ['group', 'supergroup']

    if is_group:
        # В группах бот считает сообщения и отвечает только каждое 15-е сообщение
        if chat_id not in message_counters:
            message_counters[chat_id] = 0
            
        message_counters[chat_id] += 1
        
        if message_counters[chat_id] < 15:
            update_history(chat_id, text)
            return
        else:
            message_counters[chat_id] = 0

    # 3. Сохраняем фразу в историю чата (учитывает и людей, и других ботов)
    update_history(chat_id, text)

    # 4. Режим по умолчанию
    if chat_id not in user_modes:
        user_modes[chat_id] = 'own'

    mode = user_modes[chat_id]
    
    # 5. Логика ответов
    if mode == 'echo':
        if user_history[chat_id] and len(user_history[chat_id]) > 1:
            past_phrases = [p for p in user_history[chat_id] if p != text]
            response = random.choice(past_phrases) if past_phrases else text
        else:
            response = text
            
    elif mode == 'mix':
        pool = ALL_BASE_PHRASES.copy()
        if user_history[chat_id]:
            pool.extend(user_history[chat_id])
        response = random.choice(pool)
        
    else:
        text_lower = text.lower()
        if any(word in text_lower for word in ['привет', 'здарова', 'ку', 'здаров', 'хай', 'дороу']):
            response = random.choice(GREETINGS)
        elif any(word in text_lower for word in ['код', 'питон', 'скрипт', 'ошибка', 'баг', 'сервер', 'гитхаб']):
            response = random.choice(TECH_QUOTES)
        elif any(word in text_lower for word in ['музыка', 'трек', 'вайб', 'космос', 'жизнь', 'капкут']):
            response = random.choice(VIBE_QUOTES)
        elif any(word in text_lower for word in ['дурак', 'тупой', 'кринж', 'бот', 'сука', 'блять']):
            response = random.choice(TOXIC_ROASTS)
        else:
            response = random.choice(ALL_BASE_PHRASES)

    bot.reply_to(message, response)

def update_history(chat_id, text):
    if chat_id not in user_history:
        user_history[chat_id] = []
    if text not in user_history[chat_id]:
        user_history[chat_id].append(text)
        if len(user_history[chat_id]) > 100:
            user_history[chat_id].pop(0)

if __name__ == '__main__':
    print("Бот запущен и готов к работе...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    
