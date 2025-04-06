import os
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Получаем ключи из переменных окружения
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY не установлен в переменных среды.")
if not telegram_token:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных среды.")

# Устанавливаем ключ OpenAI
openai.api_key = openai_api_key

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Задай мне вопрос по котлам Baxi.")

# Ответ на сообщение
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты помощник по ремонту котлов Baxi."},
                {"role": "user", "content": user_message}
            ]
        )
        answer = response['choices'][0]['message']['content']
    except Exception as e:
        answer = f"Ошибка при обращении к OpenAI: {e}"

    await update.message.reply_text(answer)

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен!")
    app.run_polling()
