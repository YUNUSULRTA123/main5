фimport os
import time
import threading
import schedule
import telebot
from telebot.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# Инициализация бота
API_TOKEN = os.getenv("API_TOKEN", "YOUR_API_TOKEN_HERE")
bot = telebot.TeleBot(API_TOKEN)

# Глобальные переменные
users = {}
freeid = None

# Команды '/start' и '/help'
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f"Привет! Я бот {bot.get_me().first_name}.\n"
                          "Мои команды:\n"
                          "/start - Приветствие\n"
                          "/help - Помощь\n"
                          "/find - Найти собеседника\n"
                          "/stop - Остановить поиск\n"
                          "/set <секунды> - Установить таймер\n"
                          "/unset - Удалить таймер")

# Команда '/find' - Поиск собеседника
@bot.message_handler(commands=['find'])
def find(message):
    global freeid
    chat_id = message.chat.id

    if chat_id in users:
        bot.send_message(chat_id, "Вы уже находитесь в диалоге!")
        return

    bot.send_message(chat_id, "Поиск собеседника...")
    if freeid is None:
        freeid = chat_id
    else:
        bot.send_message(chat_id, "Собеседник найден!")
        bot.send_message(freeid, "Собеседник найден!")

        users[chat_id] = freeid
        users[freeid] = chat_id
        freeid = None

# Команда '/stop' - Остановка диалога или поиска
@bot.message_handler(commands=['stop'])
def stop(message):
    global freeid
    chat_id = message.chat.id

    if chat_id in users:
        opponent = users.pop(chat_id)
        users.pop(opponent, None)
        bot.send_message(chat_id, "Диалог завершен.")
        bot.send_message(opponent, "Ваш собеседник покинул диалог.")
    elif chat_id == freeid:
        freeid = None
        bot.send_message(chat_id, "Поиск остановлен.")
    else:
        bot.send_message(chat_id, "Вы не участвуете в поиске или диалоге.")

# Обработка сообщений в диалоге
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'audio', 'document'])
def message_handler(message):
    chat_id = message.chat.id
    if chat_id in users:
        opponent = users[chat_id]
        bot.copy_message(opponent, chat_id, message.message_id)
    else:
        bot.send_message(chat_id, "Вы не в диалоге. Используйте /find для поиска собеседника.")

# Таймеры с использованием библиотеки schedule
def beep(chat_id):
    bot.send_message(chat_id, "Beep!")

@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        seconds = int(args[1])
        schedule.every(seconds).seconds.do(beep, chat_id=message.chat.id).tag(str(message.chat.id))
        bot.reply_to(message, f"Таймер установлен на каждые {seconds} секунд.")
    else:
        bot.reply_to(message, "Использование: /set <секунды>")

@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(str(message.chat.id))
    bot.reply_to(message, "Таймер удален.")

# Клавиатура WebApp
WEB_URL = "https://pytelegrambotminiapp.vercel.app"

@bot.message_handler(commands=['webapp'])
def web_app(message):
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(InlineKeyboardButton("Открыть WebApp", web_app=WebAppInfo(WEB_URL)))
    bot.send_message(message.chat.id, "Нажмите кнопку ниже для открытия WebApp", reply_markup=inline_markup)

# Фоновый процесс для выполнения задач
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    bot.infinity_polling(skip_pending=True)
