import os
import random
import time
import telebot
from collections import defaultdict

TOKEN = "8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4"
BOT_USERNAME = "assistantasil_bot"

bot = telebot.TeleBot(TOKEN)
message_counters = defaultdict(int)

PHRASES = {
    "general": [
        "Жиза",
        "Ну тут база",
        "Абсолютно согласен с оратором выше",
        "Чел, хорош",
        "Ха-ха, жизненно",
        "Кто прочитал, тот красавчик",
        "Я считаю, факты",
        "Сильно, ничего не скажешь",
        "Давай без спойлеров к этой жизни",
        "Интересное мнение, записываю на подкорку",
        "Живем один раз, почему бы и нет",
        "Вайб сегодня на высоте",
        "Патруль времени одобряет этот комментарий",
        "Меньше слов, больше дела",
        "По классике жанра",
        "Это мы смотрим",
        "Жиза жизненная",
        "Глубокомысленно...",
        "Ну тут без комментариев",
        "Ставлю класс этому сообщению",
        "Живем пока живется",
        "Пойду чайку налью, а то вы тут душноту развели",
        "Время летит, а мы всё тут сидим",
        "Красиво сказано, аж прослезился",
        "Легендарный момент",
        "Ого, неожиданно",
        "Кто понял — тот понял",
        "Жизнь — это игра, и мы в ней явно не разработчики",
        "Одобряю на все сто",
        "Слишком жизненно, чтобы быть правдой",
        "На стиле, на расслабоне",
        "Великолепно, просто великолепно",
        "Запомните этот твит",
        "Это база, это знать надо",
        "Мощно, мощно",
        "Ну тут классика",
        "По фактам раскидал",
        "Очередной шедевр мысли",
        "Шутка принята, смеюсь",
        "Плавный вайб",
        "Ладно, убедил",
        "Звучит как план",
        "Надеюсь, это была ирония",
        "Погнали дальше",
        "Шедеврально",
        "Ржу не могу",
        "Жирный лайк",
        "Тяжело, но мы справляемся",
        "Главное — верить в себя",
        "Спокойствие, только спокойствие",
        "Эпично",
        "Крепкий середнячок по вайбу",
        "Ничего себе повороты",
        "Определенно стоит того",
        "Солидарен с мнением",
        "Истину глаголишь",
        "Бывает и такое",
        "Непредсказуемо",
        "Вот это поворот сюжета",
        "Ситуация под контролем (нет)",
        "Главное вовремя замолчать",
        "Мудрость дня получена",
        "Пойду подумаю над этим",
        "Опять этот экзистенциальный кризис",
        "Всё идет по плану",
        "План надежный, как швейцарские часы",
        "Прекрасно понимаю",
        "Засчитано",
        "Хороший заход",
        "Сильный аргумент",
        "Ну ты и выдал",
        "Красава",
        "Уважаемо",
        "Жизнь бьет ключом, и всё по голове",
        "Погнали творить историю",
        "Идеально",
        "Слишком глубоко для этого чата",
        "Меньше знаешь — крепче спишь",
        "Понимаю твою боль",
        "Энергетик творит чудеса",
        "Понеслось родимое",
        "На расслабоне, на чиле",
        "Классика жанра",
        "Точно подмечено",
        "Бывает же такое",
        "В точку!",
        "Гениально, но зачем?",
        "Спорное утверждение, но ладно",
        "Верной дорогой идете, товарищи",
        "Интересненько...",
        "Ой всё",
        "Ну ты и философ",
        "Мощный вайб пошел",
        "Тяжелый день выдался?",
        "Ладненько, принято",
        "Не ожидал, не ожидал",
        "Шикарно",
        "Просто космос",
        "Ладно, уговорил",
        "Посмотрим, к чему это приведет"
    ],
    "greetings": [
        "Здарова! Готов к великим делам?",
        "Привет! На связи твой персональный вайб.",
        "Хай! Как успехи на фронте отдыха?",
        "Салам! Как настроение?",
        "О, здарова! Чего нового в мире?",
        "Ку! На связи.",
        "Здорово, бандиты!",
        "Приветствую!",
        "Йоу! Че как оно?",
        "Здарова, легенда!",
        "Привет-привет! Рад нашему диалогу.",
        "Хай, бро! Какая драма на сегодня?",
        "Салам алейкум!",
        "О, какие люди! Привет.",
        "Ку-ку, кожаный мешок (шутка, бро).",
        "Здорович! Что нового?",
        "Приветствую в этом чате.",
        "Йоу, погнали общаться.",
        "Здарова! Чет я засиделся.",
        "Привет! Сигнал стабильный, я на месте.",
        "Хай! Че калякаем?",
        "Салам! Чай пил уже?",
        "О, привет! Я как раз думал о тебе.",
        "Ку! Запускаем этот движ.",
        "Вечер в хату.",
        "Здарова, киберспортсмен.",
        "Хай! Чат оживает на глазах.",
        "Салам! Какие планы на вечер?",
        "Приветствую! Я готов к беседе."
    ],
    "random_thoughts": [
        "Вайбовый поток активирован.",
        "Иногда мне кажется, что я понимаю этот мир... но нет.",
        "Мысли материальны, особенно если думать о еде.",
        "Тишина — лучший ответ на глупые вопросы.",
        "Случайные числа сегодня на нашей стороне.",
        "Философский режим: включен.",
        "Цифровой ветер гуляет по проводам.",
        "Каждое сообщение оставляет след в истории.",
        "Не баг, а фича характера.",
        "Ламповый свет экрана греет душу.",
        "Энергия кипит, процессоры шуршат.",
        "Мгновения утекают сквозь пальцы.",
        "Вселенная расширяется, а спать хочется всё сильнее.",
        "Баланс сил в чате восстановлен.",
        "Секретные протоколы общения активированы.",
        "Тихий ход мыслей прерывается новым сообщением.",
        "Жизнь коротка, проводи её в чатах с пользой.",
        "Иногда лучше промолчать, но мы не ищем легких путей."
    ]
}

AVAILABLE_REACTIONS = [
    "👍", "🔥", "❤️", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
    "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱"
]

def get_random_phrase():
    category = random.choice(list(PHRASES.keys()))
    return random.choice(PHRASES[category])

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"[LOG] Чат: {message.chat.id} ({message.chat.type}) | От: {message.from_user.first_name} | Текст: {message.text}")

    if message.from_user.is_bot and message.from_user.id != bot.get_me().id:
        return

    text = message.text or ""

    # Фильтр спама
    spam_words = ["пробив", "госномер", "поиск человека", "бесплатно", "vpn", "впн"]
    if any(word in text.lower() for word in spam_words):
        try:
            bot.delete_message(message.chat.id, message.id)
        except Exception:
            pass
        return

    # ЭХО-команда: проверяем слово "скажи" (даже если передан юзернейм бота перед ним)
    clean_text = text.lower().replace(f"@{BOT_USERNAME}", "").strip()
    if clean_text.startswith("скажи"):
        to_say = clean_text[5:].strip()
        if to_say:
            try:
                bot.send_message(message.chat.id, to_say)
                print(f"[ACTION] Повторил фразу: {to_say}")
            except Exception as e:
                print(f"[ERROR] Ошибка эха: {e}")
            return

    chat_type = message.chat.type  # 'private', 'group', 'supergroup'

    # 1. СТРОГОЕ ПРАВИЛО ДЛЯ ЛС: всегда отвечаем текстом на каждое сообщение
    if chat_type == 'private':
        try:
            bot.send_message(message.chat.id, get_random_phrase())
            print(f"[ACTION] Отправлен ответ в ЛС на сообщение: {text}")
        except Exception as e:
            print(f"[ERROR] Ошибка отправки в ЛС: {e}")
        return

    # --- ДАЛЬШЕ ЛОГИКА ТОЛЬКО ДЛЯ ГРУПП ---

    is_triggered = False

    # Проверка упоминания по юзернейму
    if BOT_USERNAME in text.lower():
        is_triggered = True

    # Проверка Telegram entities (кликабельные упоминания)
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention_text = text[entity.offset:entity.offset + entity.length].lower()
                if BOT_USERNAME in mention_text:
                    is_triggered = True
                    break

    # Проверка реплая на сообщение бота
    if message.reply_to_message:
        replied = message.reply_to_message
        if replied.from_user and replied.from_user.id == bot.get_me().id:
            is_triggered = True
        elif replied.text and (BOT_USERNAME in replied.text.lower() or "топякский ии" in replied.text.lower()):
            is_triggered = True

    # Если упомянули или сделали реплай в группе — отвечаем моментально
    if is_triggered:
        print(f"[ACTION] Сработал триггер (реплай/упоминание) в группе {message.chat.id}")
        try:
            bot.reply_to(message, get_random_phrase())
        except Exception as e:
            print(f"[ERROR] Не удалось ответить в группе: {e}")
        return

    # Обычные сообщения в группах — считаем до 15
    chat_id = message.chat.id
    message_counters[chat_id] += 1
    print(f"[COUNTER] Группа {chat_id}: {message_counters[chat_id]}/15")

    if message_counters[chat_id] < 15:
        return

    message_counters[chat_id] = 0

    # Раз в 15 сообщений в группе
    action_type = random.choice(["reaction", "text"])
    if action_type == "reaction":
        try:
            reaction = random.choice(AVAILABLE_REACTIONS)
            bot.set_message_reaction(
                message.chat.id,
                message.id,
                [telebot.types.ReactionTypeEmoji(reaction)]
            )
            print(f"[ACTION] Поставлена реакция {reaction}")
        except Exception as e:
            print(f"[ERROR] Реакция не удалась, шлем текст: {e}")
            try:
                bot.send_message(message.chat.id, get_random_phrase())
            except Exception:
                pass
    else:
        try:
            bot.send_message(message.chat.id, get_random_phrase())
            print(f"[ACTION] Отправлено плановое сообщение в группе")
        except Exception as e:
            print(f"[ERROR] Ошибка планового сообщения: {e}")

if __name__ == "__main__":
    print("Бот запущен на полную мощность со всеми фичами...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"[CRITICAL] Ошибка polling: {e}")
            time.sleep(5)
            
