import os
import sqlite3
import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Токен твоего бота (лучше указать твой токен прямо здесь)
TOKEN = "ТВОЙ_ТОКЕН_БОТА"

# Настройки вебхука
# Сюда автоматически подставится URL от хостинга (например, Render) или укажи свой домен
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://topyak-bot.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URI = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация базы данных (SQLite) с поддержкой чатов
def init_db():
    conn = sqlite3.connect("tiktok_meter.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_users (
            user_id INTEGER,
            chat_id INTEGER,
            username TEXT,
            followers INTEGER DEFAULT 0,
            last_up INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Функция для получения или создания игрока в текущем чате
def get_or_create_user(user_id: int, chat_id: int, username: str):
    conn = sqlite3.connect("tiktok_meter.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT followers, last_up FROM chat_users WHERE user_id = ? AND chat_id = ?",
        (user_id, chat_id)
    )
    row = cursor.fetchone()
    
    if not row:
        cursor.execute(
            "INSERT INTO chat_users (user_id, chat_id, username, followers, last_up) VALUES (?, ?, ?, 0, 0)",
            (user_id, chat_id, username)
        )
        conn.commit()
        followers, last_up = 0, 0
    else:
        followers, last_up = row
        # Обновляем юзернейм на случай, если он поменялся
        cursor.execute(
            "UPDATE chat_users SET username = ? WHERE user_id = ? AND chat_id = ?",
            (username, user_id, chat_id)
        )
        conn.commit()
        
    conn.close()
    return followers, last_up

# Установка команд бота в меню
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="up", description="Фармить подписчиков"),
        BotCommand(command="stats", description="Статистика чата"),
        BotCommand(command="top", description="Топ игроков чата"),
        BotCommand(command="help", description="Помощь по боту"),
    ]
    await bot.set_my_commands(commands)

# Команда /help и /start
@dp.message(Command("start", "help"))
async def cmd_start_help(message: types.Message):
    is_private = message.chat.type == "private"
    limit_text = "⏳ Лимитов нет (личный чат)" if is_private else "⏳ Лимит сбора в этой группе: раз в 1 час 00 минут."
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏆 Топ игроков (/stats)", callback_data="show_stata")
    
    text = (
        f"🎮 **ТикТокометр-Кликер**\n\n"
        f"Твой личный виртуальный TikTok-аккаунт в этом чате.\n\n"
        f"👥 Подписчиков на балансе: **0**\n\n"
        f"{limit_text}\n\n"
        f"📌 **Команды:**\n"
        f"• `/up` — Начать игру / фармить подписчиков\n"
        f"• `/Sanineped [число]` — Передать подписчиков другу (реплаем)\n"
        f"• `/stats` — Статистика чата и твой ранг\n"
        f"• `/top` — Топ-10 игроков"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())

# Команда /up (фарм)
@dp.message(Command("up"))
async def cmd_up(message: types.Message):
    user = message.from_user
    chat = message.chat
    
    # В ЛС лимитов нет, в группах можно сделать кулдаун (например, 1 час)
    is_private = chat.type == "private"
    current_time = message.date.timestamp()
    
    followers, last_up = get_or_create_user(user.id, chat.id, user.full_name)
    
    cooldown = 3600  # 1 час в секундах
    if not is_private and (current_time - last_up < cooldown) and last_up != 0:
        left = int(cooldown - (current_time - last_up))
        minutes = left // 60
        await message.answer(f"⏳ Рано! Следующий сбор будет доступен через {minutes} мин.")
        return

    # Начисляем случайное количество подписчиков (например, от 100 до 500)
    gained = random.randint(100, 500)
    new_followers = followers + gained
    
    conn = sqlite3.connect("tiktok_meter.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chat_users SET followers = ?, last_up = ? WHERE user_id = ? AND chat_id = ?",
        (new_followers, current_time, user.id, chat.id)
    )
    conn.commit()
    conn.close()
    
    await message.answer(f"🎉 Вы успешно пофармили! Получено: **+{gained}** 👥\nВсего подписчиков: **{new_followers}**", parse_mode="Markdown")

# Команда /Sanineped (передача подписчиков реплаем с рандомным штрафом 10–50%)
@dp.message(Command("Sanineped"))
async def cmd_sanineped(message: types.Message):
    if not message.reply_to_message:
        await message.answer("⚠️ Чтобы передать подписчиков, ответьте командой `/Sanineped [число]` на сообщение того игрока, кому хотите передать!")
        return
        
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("⚠️ Укажите количество подписчиков для передачи, например: `/Sanineped 500`", parse_mode="Markdown")
        return
        
    amount = int(args[1])
    sender = message.from_user
    receiver = message.reply_to_message.from_user
    chat = message.chat
    
    if sender.id == receiver.id:
        await message.answer("❌ Нельзя передавать подписчиков самому себе!")
        return
        
    sender_followers, _ = get_or_create_user(sender.id, chat.id, sender.full_name)
    
    if sender_followers < amount:
        await message.answer(f"❌ У вас недостаточно подписчиков! На балансе: {sender_followers} 👥")
        return
        
    # Рассчитываем случайный штраф от 10% до 50%
    penalty_percent = random.randint(10, 50)
    lost_amount = int(amount * (penalty_percent / 100))
    final_amount = amount - lost_amount
    
    # Обновляем баланс отправителя (минус вся сумма)
    get_or_create_user(receiver.id, chat.id, receiver.full_name) # создаем получателя, если не было
    
    conn = sqlite3.connect("tiktok_meter.db")
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE chat_users SET followers = followers - ? WHERE user_id = ? AND chat_id = ?",
        (amount, sender.id, chat.id)
    )
    # Получателю падает сумма с учетом штрафа комиссионных
    cursor.execute(
        "UPDATE chat_users SET followers = followers + ? WHERE user_id = ? AND chat_id = ?",
        (final_amount, receiver.id, chat.id)
    )
    conn.commit()
    conn.close()
    
    await message.answer(
        f"💸 **Перевод выполнен!**\n"
        f"• Отправитель: {sender.full_name} (-{amount} 👥)\n"
        f"• Комиссия системы ({penalty_percent}%): сгорело {lost_amount} 👥\n"
        f"• Получил игрок {receiver.full_name}: **+{final_amount}** 👥",
        parse_mode="Markdown"
    )

# Команда /top
@dp.message(Command("top", "stats"))
async def cmd_top(message: types.Message):
    chat = message.chat
    conn = sqlite3.connect("tiktok_meter.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, followers FROM chat_users WHERE chat_id = ? ORDER BY followers DESC LIMIT 10",
        (chat.id,)
    )
    top_users = cursor.fetchall()
    conn.close()
    
    if not top_users:
        await message.answer("🏆 В этом чате еще никто не фармил подписчиков. Напишите `/up`, чтобы начать!", parse_mode="Markdown")
        return
        
    text = "🏆 **Топ-10 тиктокеров этого чата:**\n\n"
    for idx, (uname, f_count) in enumerate(top_users, start=1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        text += f"{medal} {uname or 'Игрок'} — **{f_count}** подписчиков 👥\n"
        
    await message.answer(text, parse_mode="Markdown")

# Событие при старте вебхука
async def on_startup(bot: Bot):
    await set_commands(bot)
    await bot.set_webhook(WEBHOOK_URI, drop_pending_updates=True)
    print(f"Вебхук успешно установлен: {WEBHOOK_URI}")

# Главная функция запуска через aiohttp сервер
def main():
    app = web.Application()

    # Регистрация обработчика вебхуков aiogram
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_handler.register(app, WEBHOOK_PATH)

    # Настройка приложения
    setup_application(app, dp, bot=bot)
    dp.startup.register(on_startup)

    # Получаем порт из окружения хостинга (Render стандартно передает PORT)
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
  
