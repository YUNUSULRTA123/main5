import telebot  

import time, threading, schedule
from telebot import TeleBot

API_TOKEN = '8119500631:AAHDitnnXOQOw--jbpbgLmS4bOx_SK7LN9E'
bot = TeleBot(API_TOKEN)



keys = ["1","2","3","4","5","6","7","8","9","0","q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","z","x","c","v","b","n","m"]
symbols = ["1","2","3","4","5","6","7","8","9","0","!","@","#","$","%","^","&","*","(",")","\'","\"","/","\\",",",".",";",":"]

def keyboard(key_type="Normal"):
    markup = ReplyKeyboardMarkup(row_width=10)
    if key_type == "Normal":
        row = [KeyboardButton(x) for x in keys[:10]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in keys[10:20]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in keys[20:29]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in keys[29:]]
        markup.add(*row)
        markup.add(KeyboardButton("Caps Lock"),KeyboardButton("Symbols"),KeyboardButton("🔙Delete"),KeyboardButton("✅Done"))
    elif key_type == "Symbols":
        row = [KeyboardButton(x) for x in symbols[:10]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in symbols[10:20]]
        markup.add(*row)
        row = [KeyboardButton(x) for x in symbols[20:]]
        markup.add(*row)
        markup.add(KeyboardButton("Caps Lock"),KeyboardButton("Normal"),KeyboardButton("🔙Delete"),KeyboardButton("✅Done"))
    else:
        row = [KeyboardButton(x.upper()) for x in keys[:10]]
        markup.add(*row)
        row = [KeyboardButton(x.upper()) for x in keys[10:20]]
        markup.add(*row)
        row = [KeyboardButton(x.upper()) for x in keys[20:29]]
        markup.add(*row)
        row = [KeyboardButton(x.upper()) for x in keys[29:]]
        markup.add(*row)
        markup.add(KeyboardButton("Normal"),KeyboardButton("Symbols"),KeyboardButton("🔙Delete"),KeyboardButton("✅Done"))
    return markup

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id,"You can use the keyboard",reply_markup=keyboard())

@bot.message_handler(func=lambda message:True)
def all_messages(message):
    if message.text == "✅Done":
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,"Done with Keyboard",reply_markup=markup)
    elif message.text == "Symbols":
        bot.send_message(message.from_user.id,"Special characters",reply_markup=keyboard("Symbols"))
    elif message.text == "Normal":
        bot.send_message(message.from_user.id,"Normal Keyboard",reply_markup=keyboard("Normal"))
    elif message.text == "Caps Lock":
        bot.send_message(message.from_user.id,"Caps Lock",reply_markup=keyboard("Caps"))
    elif message.text == "🔙Delete":
        bot.delete_message(message.from_user.id,message.message_id)
    else:
        bot.send_message(message.chat.id,message.text)



# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

# The `users` variable is needed to contain chat ids that are either in the search or in the active dialog, like {chat_id, chat_id}
users = {}
# The `freeid` variable is needed to contain chat id, that want to start conversation
# Or, in other words: chat id of user in the search
freeid = None

# `/start` command handler
#
# That command only sends you 'Just use /find command!'
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.chat.id, 'Just use /find command!')

# `/find` command handler
#
# That command finds opponent for you
#
# That command according to the following principle:
# 1. You have written `/find` command
# 2. If you are already in the search or have an active dialog, bot sends you 'Shut up!'
# 3. If not:
#   3.1. Bot sends you 'Finding...'
#   3.2. If there is no user in the search:
#       3.2.2. `freeid` updated with `your_chat_id`
#   3.3. If there is user in the search:
#       3.3.1. Both you and the user in the search recieve the message 'Founded!'
#       3.3.2. `users` updated with a {user_in_the_search_chat_id, your_chat_id}
#       3.3.3. `users` updated with a {your_chat_id, user_in_the_search_id}
#       3.3.4. `freeid` updated with `None`
@bot.message_handler(commands=['find'])
def find(message: types.Message):
    global freeid

    if message.chat.id not in users:
        bot.send_message(message.chat.id, 'Finding...')

        if freeid is None:
            freeid = message.chat.id
        else:
            # Question:
            # Is there any way to simplify this like `bot.send_message([message.chat.id, freeid], 'Founded!')`?
            bot.send_message(message.chat.id, 'Founded!')
            bot.send_message(freeid, 'Founded!')

            users[freeid] = message.chat.id
            users[message.chat.id] = freeid
            freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'Shut up!')

# `/stop` command handler
#
# That command stops your current conversation (if it exist)
#
# That command according to the following principle:
# 1. You have written `/stop` command
# 2. If you are not have active dialog or you are not in search, bot sends you 'You are not in search!'
# 3. If you are in active dialog:
#   3.1. Bot sends you 'Stopping...'
#   3.2. Bot sends 'Your opponent is leavin`...' to your opponent
#   3.3. {your_opponent_chat_id, your_chat_id} removes from `users`
#   3.4. {your_chat_id, your_opponent_chat_id} removes from `users`
# 4. If you are only in search:
#   4.1. Bot sends you 'Stopping...'
#   4.2. `freeid` updated with `None`
@bot.message_handler(commands=['stop'])
def stop(message: types.Message):
    global freeid

    if message.chat.id in users:
        bot.send_message(message.chat.id, 'Stopping...')
        bot.send_message(users[message.chat.id], 'Your opponent is leavin`...')

        del users[users[message.chat.id]]
        del users[message.chat.id]
        
        print(users, freeid) # Debug purpose, you can remove that line
    elif message.chat.id == freeid:
        bot.send_message(message.chat.id, 'Stopping...')
        freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'You are not in search!')

# message handler for conversation
#
# That handler needed to send message from one opponent to another
# If you are not in `users`, you will recieve a message 'No one can hear you...'
# Otherwise all your messages are sent to your opponent
#
# Questions:
# 1. Is there any way to improve readability like `content_types=['all']`?
# 2. Is there any way to register this message handler only when i found the opponent?
@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def chatting(message: types.Message):
    if message.chat.id in users:
        bot.copy_message(users[message.chat.id], users[users[message.chat.id]], message.id)
    else:
        bot.send_message(message.chat.id, 'No one can hear you...')

bot.infinity_polling(skip_pending=True)


from telebot.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

WEB_URL = "https://pytelegrambotminiapp.vercel.app" 



@bot.message_handler(commands=["start"])
def start(message):
    reply_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_keyboard_markup.row(KeyboardButton("Start MiniApp", web_app=WebAppInfo(WEB_URL)))

    inline_keyboard_markup = InlineKeyboardMarkup()
    inline_keyboard_markup.row(InlineKeyboardButton('Start MiniApp', web_app=WebAppInfo(WEB_URL)))

    bot.reply_to(message, "Click the bottom inline button to start MiniApp", reply_markup=inline_keyboard_markup)
    bot.reply_to(message, "Click keyboard button to start MiniApp", reply_markup=reply_keyboard_markup)

@bot.message_handler(content_types=['web_app_data'])
def web_app(message):
    bot.reply_to(message, f'Your message is "{message.web_app_data.data}"')

bot.infinity_polling()
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Use /set <seconds> to set a timer")



def beep(chat_id) -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text='Beep!')


@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
    else:
        bot.reply_to(message, 'Usage: /set <seconds>')


@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(message.chat.id)


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)

# Инициализация бота с использованием его токена  
bot = telebot.TeleBot("8119500631:AAHDitnnXOQOw--jbpbgLmS4bOx_SK7LN9E")  

# Обработчик команды '/start' и '/hello'  
@bot.message_handler(commands=['start', 'hello'])  
def send_welcome(message):  
bot.reply_to(message, f'Привет! Я бот {bot.get_me().first_name}!')  

# Обработчик команды '/heh'  
@bot.message_handler(commands=['heh'])  
def send_heh(message):  
count_heh = int(message.text.split()[1]) if len(message.text.split()) > 1 else 5  
bot.reply_to(message, "he" * count_heh)  
text_messages = {
    'welcome':
        u'Please welcome {name}!\n\n'
        u'This chat is intended for questions about and discussion of the pyTelegramBotAPI.\n'
        u'To enable group members to answer your questions fast and accurately, please make sure to study the '
        u'project\'s documentation (https://github.com/eternnoir/pyTelegramBotAPI/blob/master/README.md) and the '
        u'examples (https://github.com/eternnoir/pyTelegramBotAPI/tree/master/examples) first.\n\n'
        u'I hope you enjoy your stay here!',

    'info':
        u'My name is TeleBot,\n'
        u'I am a bot that assists these wonderful bot-creating people of this bot library group chat.\n'
        u'Also, I am still under development. Please improve my functionality by making a pull request! '
        u'Suggestions are also welcome, just drop them in this group chat!',

    'wrong_chat':
        u'Hi there!\nThanks for trying me out. However, this bot can only be used in the pyTelegramAPI group chat.\n'
        u'Join us!\n\n'
        u'https://telegram.me/joinchat/067e22c60035523fda8f6025ee87e30b'
}

if "TELEBOT_BOT_TOKEN" not in os.environ or "GROUP_CHAT_ID" not in os.environ:
    raise AssertionError("Please configure TELEBOT_BOT_TOKEN and GROUP_CHAT_ID as environment variables")

bot = telebot.AsyncTeleBot(os.environ["TELEBOT_BOT_TOKEN"])
GROUP_CHAT_ID = int(os.environ["GROUP_CHAT_ID"])


def is_api_group(chat_id):
    return chat_id == GROUP_CHAT_ID


@bot.message_handler(func=lambda m: True, content_types=['new_chat_participant'])
def on_user_joins(message):
    if not is_api_group(message.chat.id):
        return

    name = message.new_chat_participant.first_name
    if hasattr(message.new_chat_participant, 'last_name') and message.new_chat_participant.last_name is not None:
        name += u" {}".format(message.new_chat_participant.last_name)

    if hasattr(message.new_chat_participant, 'username') and message.new_chat_participant.username is not None:
        name += u" (@{})".format(message.new_chat_participant.username)

    bot.reply_to(message, text_messages['welcome'].format(name=name))


@bot.message_handler(commands=['info', 'help'])
def on_info(message):
    if not is_api_group(message.chat.id):
        bot.reply_to(message, text_messages['wrong_chat'])
        return

    bot.reply_to(message, text_messages['info'])


@bot.message_handler(commands=["ping"])
def on_ping(message):
    bot.reply_to(message, "Still alive and kicking!")


@bot.message_handler(commands=['start'])
def on_start(message):
    if not is_api_group(message.chat.id):
        bot.reply_to(message, text_messages['wrong_chat'])
        return


def listener(messages):
    for m in messages:
        print(str(m))


bot.set_update_listener(listener)
# Запуск бота  
bot.polling()
