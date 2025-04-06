from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import sqlite3
from openai import OpenAI

import os
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔍 Поиск в базе данных
def search_in_db(query):
    conn = sqlite3.connect("knowledge_base.db")
    c = conn.cursor()
    try:
        c.execute('''
            SELECT pdf_name, content FROM pdf_data 
            WHERE content LIKE ?
        ''', ('%' + query + '%',))
        results = c.fetchall()
    except Exception as e:
        print(f"Ошибка при запросе к базе: {e}")
        results = None
    finally:
        conn.close()
    return results if results else None

# 🧠 Запрос к GPT
def ask_gpt(query):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты технический помощник для слесарей, отвечай кратко и по делу."},
                {"role": "user", "content": query},
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка GPT: {e}"

# 💬 Обработка входящих сообщений
async def handle_message(update: Update, context):
    query = update.message.text
    results = search_in_db(query)

    if results:
        response = "Вот что я нашел в базе знаний:\n"
        for pdf_name, content in results:
            response += f"\n📄 Документ: {pdf_name}\n📝 {content[:500]}...\n"
    else:
        gpt_answer = ask_gpt(query)
        response = f"В базе ничего не найдено, вот ответ от нейросети:\n\n{gpt_answer}"

    # Разбивка длинного ответа
    max_len = 4000
    for i in range(0, len(response), max_len):
        await update.message.reply_text(response[i:i+max_len])

# 🚀 Запуск бота
def main():
    application = Application.builder().token("7595091573:AAGEwZEgJtGQXDyjejHz8Ln00-0v5p1I2TA").build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(timeout=30)

if __name__ == '__main__':
    main()
