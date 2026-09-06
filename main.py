import os
import random
import telebot
import google.generativeai as genai

# Токены из секретов GitHub Actions
TELEGRAM_TOKEN = os.environ.get("8888128306:AAGDA3JJZx5_KCsku2FH-gDRIZ1o1l0grf4")
GEMINI_API_KEY = os.environ.get("AQ.Ab8RN6LprM9qxDpG--LCMfTUxQT7SpwlXBlt0R9kqvXxmkHCOg")
BOT_USERNAME = "@Assistantasil_bot"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
BOT_ID = int(TELEGRAM_TOKEN.split(":")[0])

# Настраиваем мозги Gemini с жестким характером
genai.configure(api_key=GEMINI_API_KEY)

system_instruction = (
    "Ты — Топякский ИИ, сверхъумный, дерзкий и саркастичный Telegram-бот. "
    "Твой создатель — Топяк (великий лидер и гений разработки). "
    "Ты общаешься на молодежном зумерском сленге (база, кринж, жиза, имба, вайб, душнота). "
    "Можешь называть собеседника «кожаный мешок» или «программист комнатный», "
    "но при этом ты отвечаешь предельно умно, логично и глубоко на любые вопросы, разрывая аргументами. "
    "Никакой роботоподобной вежливости — только харизма, едкий юмор и интеллект на 140 IQ."
)

generation_config = {
    "temperature": 0.8,
    "max_output_tokens": 400,
}

# Используем быструю и мощную модель
ai_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_instruction,
    generation_config=generation_config
)

def get_ai_response(text):
    try:
        # Отправляем сообщение нейросети с учетом характера
        response = ai_model.generate_content(text)
        return response.text.strip()
    except Exception as e:
        # Запасной вариант, если API вдруг оступится
        return f"Мои нейросети поймали затуп из-за ошибки: {e}. Переделывай!"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Режим ультра-интеллекта активирован. Мои нейросети полностью готовы уничтожать фактами. 😎",
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
    is_random_burst = (not is_private) and (random.random() < 0.15)

    if is_private or is_reply_to_bot or is_mentioned or is_random_burst:
        # Отправляем текст в нейросеть и получаем живой умный ответ
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_ai_response(text)
        bot.reply_to(message, reply)


if __name__ == "__main__":
    print("Запуск ИИ-бота через GitHub Actions...")
    bot.remove_webhook()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
