#built-in modules
from time import sleep

#local package import
from cowin import bot, config, cur, func

#needs to install using pip
import telebot
from telebot.types import InlineKeyboardMarkup

def aurthorize(message):
    return True if str(message.chat.id) in config.ADMINS_LIST_DICT.keys() else False

@bot.message_handler(chat_types=['private'], commands=['notify'])
def notify_all(message):
    if aurthorize(message):
        msg = bot.send_message(message.chat.id, '<b>Send Post or Message to Notify users !!</b>')
        bot.register_next_step_handler(msg, process_notifications)

def process_notifications(message):
    try:
        count_total = 0
        count_success = 0
        users = cur.execute("select id from users").fetchall()
        for user in users:
            send_to = user[0]
            count_total += 1
            if str(send_to)[0] == '-':
                continue
            try:
                keyboard = InlineKeyboardMarkup(keyboard = message.reply_markup.keyboard if message.reply_markup else None)
                if message.content_type == 'text':
                    bot.send_message(send_to, message.html_text, reply_markup=keyboard)
                elif message.content_type == 'video':
                    bot.send_video(send_to, message.video.file_id, caption=message.html_caption, reply_markup=keyboard)
                elif message.content_type == 'photo':
                    bot.send_photo(send_to, message.photo[len(message.photo) - 1].file_id, caption=message.html_caption, reply_markup=keyboard)
                elif message.content_type == 'document':
                    bot.send_document(send_to, message.document.file_id, caption=message.html_caption, reply_markup=keyboard)
                count_success += 1
            except:
                continue
        bot.send_message(message.chat.id, f'Notified to {count_success}/{count_total}.')
    except Exception as e:
        bot.send_message(config.LOG_GRP, f'Exception in {func.whoami()} Function :- {e}')
        sleep(5)

@bot.message_handler(chat_types=['private'], commands=['message_to'])
def admins_message(message):
    try:
        if aurthorize(message):
            if len(message.text.split()) > 1:
                send_to = message.text.split()[1].strip()
                msg = bot.send_message(message.chat.id, '<b>Ok now send ur message (text only) !!</b>')
                bot.register_next_step_handler(msg, process_admin_message, send_to)
    except Exception as e:
        bot.send_message(config.LOG_GRP, f'Exception in {func.whoami()} Function :- {e}')

def process_admin_message(message, send_to):
    try:
        bot.send_message(send_to, f'<b>Message from Admin :-</b> {message.html_text}')
        bot.send_message(message.chat.id, 'Message Sent 👍')
    except telebot.apihelper.ApiTelegramException as e:
        error = str(e.result_json['description'])
        bot.send_message(message.chat.id, error)