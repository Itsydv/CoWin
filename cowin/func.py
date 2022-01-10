#built-in modules
from time import sleep
import string, datetime, inspect, math, os

#needs to install using pip
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

#local package import
from cowin import bot, config, bot_handler, log, conn, cur
from cowin.config import Constants
from cowin.pull_data import CoWinAPI

cowin_ins = CoWinAPI()

def today() -> str:
    return datetime.datetime.now().strftime(Constants.DD_MM_YYYY)

def error_handler(error, function_name):
    bot.send_message(config.LOG_GRP, f'Exception in {function_name} Function :- {error}')

def exception_handler(error, message, function_name):
    try:
        error = str(error.result_json['description'])
        timeout = 0
        if error[:30].lower() == 'too many requests: retry after':
            timeout = int(error[31:].strip())
            error = f'Do not Flood, max limit 20 requests per minute, wait for {timeout} sec.'
        bot.send_message(message.chat.id, f"<b>{string.capwords(error)}</b>")
        if timeout:
            sleep(timeout)
    except Exception as e:
        bot.send_message(config.LOG_GRP, f'Exception in {whoami()} while Handling "{function_name}" Function :- {e}')
        
def whoami():
    return inspect.stack()[1][3]

def pull_daily_slots(chat_id, location_param, age, vaccine, fee_type, dose):
    try:
        if len(str(location_param)) == 6:
            data = cowin_ins.get_availability_by_pincode(str(location_param))
        else:
            data = cowin_ins.get_availability_by_district(str(location_param))
        if not data:
            bot.send_message(chat_id, 'We are experiencing some issues please try again in a few moment or let developer know about it, use /reportbug')
            return None
        dose_cap = f"available_capacity_dose{dose}"
        result_count = False
        found = False
        for center_no in range(len(data.get('sessions'))):
            data_ex = data.get('sessions')[center_no]
            if data_ex.get('fee_type') == fee_type.capitalize():
                msg_to_send = f'<b>Name:- </b>{data_ex["name"]} \n' + f'<b>Address:- </b>{data_ex["address"]} \n' + f'<b>Pincode:- </b>{data_ex["pincode"]}\n' + f'<b>District:- </b>{data_ex["district_name"]} \n' + f'<b>Minimum age:- </b>{data_ex["min_age_limit"]}\n' + f'({data_ex["vaccine"]} - {dose_cap[19:].capitalize()}) \n' + f'<b>Fee-type:- </b>{fee_type.capitalize()}\n'
                if data_ex["min_age_limit"] == int(age) and data_ex["vaccine"] == vaccine.upper() and data_ex[dose_cap] > 0:
                    result_count = True
                    found = True
                    msg_to_send += f'\nDate:- {data_ex["date"]} \n' + f'Available Doses:- {data_ex[dose_cap]} \n'
                if result_count:
                    msg_to_send += '\n\n<code>Booking Vaccine slot is a game of Time</code>\n\nHurry !! Book your slot at <a href="https://selfregistration.cowin.gov.in/">CoWIN Online</a> now. Otherwise someone other will grab It!'
                    keyboard = InlineKeyboardMarkup()
                    keyboard.row(InlineKeyboardButton('Book Slots', url='https://selfregistration.cowin.gov.in'))
                    bot.send_message(chat_id, msg_to_send, reply_markup=keyboard)
                    result_count = False
        if not found:
            bot.send_message(chat_id, "<b>Sorry !! But there're no slots available matching your Preferences</b>")
        
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')
        
def pull_weekly_slots(chat_id, location_param, age, vaccine, fee_type, dose):
    try:
        if len(str(location_param)) == 6:
            data = cowin_ins.get_availability_by_pincode_week(str(location_param))
        else:
            data = cowin_ins.get_availability_by_district_week(str(location_param))
        if not data:
            bot.send_message(chat_id, 'We are experiencing some issues please try again in a few moment or let developer know about it, use /reportbug')
            return None     
        dose_cap = f"available_capacity_dose{dose}"
        result_count = False
        found = False
        if data.get('centers'):
            data = data.get('centers')
        else:
            data = data.get('sessions')
        for center_no in range(len(data)):
            data_ex = data[center_no]
            if data_ex.get('fee_type') == fee_type.capitalize():
                data_in = data_ex.get('sessions')
                msg_to_send = f'<b>Name:- </b>{data_ex["name"]} \n' + f'<b>Address:- </b>{data_ex["address"]} \n' + f'<b>Pincode:- </b>{data_ex["pincode"]}\n' + f'<b>District:- </b>{data_ex["district_name"]} \n' + f'<b>Minimum age:- </b>{data_in[0]["min_age_limit"]}\n' + f'({data_in[0]["vaccine"]} - {dose_cap[19:].capitalize()}) \n' + f'<b>Fee-type:- </b>{fee_type.capitalize()}\n'
                for session_no in range(len(data_in)):
                    if data_in[session_no]["min_age_limit"] == int(age) and data_in[session_no]["vaccine"] == vaccine.upper() and data_in[session_no][dose_cap] > 4:
                        result_count = True
                        found = True
                        msg_to_send += f'\nDate:- {data_in[session_no]["date"]} \n' + f'Available Doses:- {data_in[session_no][dose_cap]} \n'
                if result_count:
                    msg_to_send += '\n\n<code>Booking Vaccine slot is a game of Time</code>\n\nHurry !! Book your slot at <a href="https://selfregistration.cowin.gov.in/">CoWIN Online</a> now. Otherwise someone other will grab It!'
                    keyboard = InlineKeyboardMarkup()
                    keyboard.row(InlineKeyboardButton('Book Slots', url='https://selfregistration.cowin.gov.in'))
                    bot.send_message(chat_id, msg_to_send, reply_markup=keyboard)
                    result_count = False
        if not found:
            bot.send_message(chat_id, "<b>Sorry !! But there're no slots available matching your Preferences</b>")
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')

def arrange_data_in_column(data):
    rows = math.ceil(len(data)/2)
    main_list = []
    for i in range(rows):
        try:
            main_list.append([data[2*i], data[2*i+1]])
        except:
            main_list.append([data[2*i]])
    return main_list
        
def register_user(message):
    try:
        result = cur.execute(f"Select * from users where id = {message.chat.id}").fetchone()
        if not result:
            with conn:
                username = '@' + str(message.chat.username) if message.chat.username else str(message.chat.first_name) if message.chat.first_name else str(message.chat.id)
                cur.execute(f"Insert into users (id, username, date) values ({message.chat.id}, '{username}', '{str(datetime.date.today())}')")
        return True
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')

def process_district(message, district=None):
    try:
        with conn:
            cur.execute(f"update users set district = '{district}' where id = {message.chat.id}")
        bot.delete_message(message.chat.id, message.message_id)
        result = cur.execute(f"Select district from users where id = {message.chat.id}").fetchone()
        if result:
            bot.send_message(message.chat.id, f'Done !! Your District Code is {result[0]}')
            complete_detail(message)
            return None
        bot.send_message(message.chat.id, '<b>Something went wrong Please try again !!</b>')
        bot_handler.add_states(message)
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')
    
def process_age(message, age):
    try:
        with conn:
            cur.execute(f"update users set age = '{age}' where id = {message.chat.id}")
        bot.delete_message(message.chat.id, message.message_id)
        result = cur.execute(f"Select age from users where id = {message.chat.id}").fetchone()
        if result:
            bot.send_message(message.chat.id, f'Done !! Your Age is set to {result[0]}+')
            complete_detail(message)
            return None
        bot.send_message(message.chat.id, 'Something went wrong Please try again !!')
        bot_handler.add_age(message)
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')

def process_vaccine(message, vaccine):
    try:
        bot.delete_message(message.chat.id, message.message_id)
        with conn:
            cur.execute(f"update users set vaccine = '{vaccine}' where id = {message.chat.id}")
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton('Free', callback_data='fee-free'),
            InlineKeyboardButton('Paid', callback_data='fee-paid')
        )
        bot.send_message(message.chat.id, 'Select Fee-type :-', reply_markup=keyboard)
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')

def process_fee_type(message, fee_type):
    try:
        bot.delete_message(message.chat.id, message.message_id)
        with conn:
            cur.execute(f"update users set fee = '{fee_type}' where id = {message.chat.id}")
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton('Dose - 1 ', callback_data='dose-1'),
            InlineKeyboardButton('Dose - 2', callback_data='dose-2')
        )
        bot.send_message(message.chat.id, 'Select Dose :-', reply_markup=keyboard)
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')

def process_dose(message, dose):
    try:
        bot.delete_message(message.chat.id, message.message_id)
        with conn:
            cur.execute(f"update users set dose = '{dose}' where id = {message.chat.id}")
        result = cur.execute(f"Select vaccine, fee, dose from users where id = {message.chat.id}").fetchone()
        if result:
            bot.send_message(message.chat.id, f'Preferences set to {result[1].capitalize()} {result[0].upper()} Dose {result[2]}. \n\nYou can always change them by using /preferences command.')
            bot.send_message(message.chat.id, 'Data updation process Succesful. Now you can use /gettodayslots or /getweeklyslots command.')
            complete_detail(message)
            return None
        bot.send_message(message.chat.id, 'Something went wrong Please try again !!')
        bot_handler.add_preferences(message)
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')
    
def complete_detail(message):
    try:
        if register_user(message):
            result = cur.execute(f"Select district, age, vaccine, fee, dose from users where id = {message.chat.id}").fetchone()
            district_id = result[0]
            if district_id == 'None':
                bot_handler.add_states(message)
            else:
                age = result[1]
                if age == 'None':
                    bot_handler.add_age(message)
                else:
                    dose = result[4]
                    if dose == 'None':
                        bot_handler.add_preferences(message)
            result = cur.execute(f"Select district, age, vaccine, fee, dose from users where id = {message.chat.id}").fetchone()
            return result
        complete_detail(message)
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')

def handle_cmd(message):
    try:
        if message.text.strip() == '/start':
            bot_handler.start_command(message)
        elif message.text.strip() == '/help':
            bot_handler.help_command(message)
        elif message.text.strip() == '/policy':
            bot_handler.privacy_policy(message)
        elif message.text.strip() == '/notify':
            log.notify_all(message)
        else:
            bot.send_message(message.chat.id, 'Operation Cancelled')
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')