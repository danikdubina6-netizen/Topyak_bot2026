import os
import random
import threading
import telebot
from telebot import types
from telebot.types import ReactionTypeEmoji

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Получаем ID самого бота при старте
BOT_ID = None
try:
    BOT_ID = bot.get_me().id
except Exception:
    pass

# Хранилища состояний, памяти и счетчиков
user_modes = {}       # Режимы работы (own, echo, mix) для чатов
user_history = {}     # Память: история фраз
message_counters = {} # Счетчик обычных сообщений для лимита в 15 штук
active_games = {}     # Активные мини-игры в чатах

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

# Набор реакций для авто-реакций (Фича №1)
AVAILABLE_REACTIONS = ["🔥", "👍", "👎", "💩", "😱", "🕊", "🤡", "⚡️", "🌚"]

# База для мини-игры "Угадай песню/цитату" (Фича №4)
QUIZ_QUESTIONS = [
    {"question": "Какая группа исполняет бессмертный хит про «Группу крови на рукаве»?", "answer": "кино"},
    {"question": "В каком приложении на ПК создаются лучшие треки дома?", "answer": "капкут"},
    {"question": "Что великое и беспощадное иногда бунтует в GitHub?", "answer": "раннеры"},
    {"question": "Какая оценка IQ идеально подходит кодеку Топяка?", "answer": "140"}
]

# Клавиатура с выбором режимов
def get_settings_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🗣 Говорить свои фразы (база бота)", callback_data="mode_own"),
        types.InlineKeyboardButton("🔄 Повторять чужие фразы (из истории)", callback_data="mode_echo"),
        types.InlineKeyboardButton("🔀 И то и то (Микс вариантов)", callback_data="mode_mix"),
        types.InlineKeyboardButton("🎮 Сыграть в угадайку", callback_data="start_quiz")
    )
    return markup

@bot.message_handler(commands=['start', 'help', 'mode', 'quiz'])
def send_welcome(message):
    chat_id = message.chat.id
    current_mode = user_modes.get(chat_id, 'own')
    
    if message.text.startswith('/quiz'):
        start_quiz_game(message)
        return
    
    mode_names = {
        'own': '🗣 Говорить свои фразы',
        'echo': '🔄 Повторять чужие фразы (из истории)',
        'mix': '🔀 И то и то (Микс)'
    }
    
    welcome_text = (
        f"🤖 **Топякский ИИ** на связи.\n"
        f"Текущий режим: *{mode_names.get(current_mode, 'Свои фразы')}*\n\n"
        f"Настрой бота кнопками ниже или запусти игру:"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_settings_keyboard(chat_id), parse_mode='Markdown')

def start_quiz_game(message):
    chat_id = message.chat.id
    q = random.choice(QUIZ_QUESTIONS)
    active_games[chat_id] = q['answer'].lower()
    bot.send_message(chat_id, f"🎮 **Мини-игра Угадайка за запущена!**\n\nВопрос: *{q['question']}*\n\nНапиши ответ прямо в чат!")

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
    elif data == 'start_quiz':
        bot.answer_callback_query(call.id, "Игра началась!")
        start_quiz_game(call.message)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_messages(message):
    global BOT_ID
    if not BOT_ID:
        try:
            BOT_ID = bot.get_me().id
        except Exception:
            pass

    if BOT_ID and message.from_user.id == BOT_ID:
        return

    chat_id = message.chat.id
    text = message.text
    if not text:
        return

    # Проверка ответов на мини-игру (Фича №4)
    if chat_id in active_games:
        if text.lower().strip() == active_games[chat_id]:
            bot.reply_to(message, "🎉 Красава! Ты абсолютно прав, ответ засчитан!")
            del active_games[chat_id]
            return

    # Проверяем, ответили ли на сообщение бота или затегали его
    is_replied_to_bot = (
        message.reply_to_message 
        and message.reply_to_message.from_user 
        and BOT_ID 
        and message.reply_to_message.from_user.id == BOT_ID
    )
    is_mentioned = BOT_ID and f"@{bot.get_me().username}" in text
    is_addressed_to_bot = is_replied_to_bot or is_mentioned

    if text.lower().startswith('скажи '):
        phrase_to_say = text[6:].strip()
        if phrase_to_say:
            bot.reply_to(message, phrase_to_say)
        return

    is_group = message.chat.type in ['group', 'supergroup']

    if is_group and not is_addressed_to_bot:
        if chat_id not in message_counters:
            message_counters[chat_id] = 0
            
        message_counters[chat_id] += 1
        update_history(chat_id, text)
        
        if message_counters[chat_id] < 15:
            return
        else:
            message_counters[chat_id] = 0
            # ФИЧА №1: Вместо ответа текстом бот может молча поставить реакцию на сообщение!
            if random.choice([True, False]):
                try:
                    chosen_emoji = random.choice(AVAILABLE_REACTIONS)
                    bot.set_message_reaction(chat_id, message.id, [ReactionTypeEmoji(emoji=chosen_emoji)], is_big=False)
                except Exception:
                    pass
                return

    update_history(chat_id, text)

    if chat_id not in user_modes:
        user_modes[chat_id] = 'own'

    mode = user_modes[chat_id]
    
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
    print("Бот запущен с авто-реакциями и угадайкой...")
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
                     
