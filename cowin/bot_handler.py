#built-in modules
import datetime, os
from hashlib import sha256

#needs to install using pip
import telebot, requests
from telebot import custom_filters
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

#local import
from cowin import bot, conn, cur, config, func, log
from cowin.pull_data import CoWinAPI
from cowin.config import Constants

cowin = CoWinAPI()

@bot.message_handler(state="*", commands='cancel')
def any_state(message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "<b>Operation Cancelled.</b>")
    bot.delete_state(message.chat.id)

@bot.message_handler(chat_types=['private'], commands=['start'])
def start_command(message):
    try:
        keyboard = InlineKeyboardMarkup()
        username = message.chat.first_name if message.chat.first_name else str('@' + message.chat.username) if message.chat.username else str(message.chat.id)
        result = cur.execute(f"select * from users where id = {message.chat.id}").fetchone()
        #if user already registered
        if result:
            keyboard.row(
                InlineKeyboardButton('Update Preferences', callback_data='preferences'),
                InlineKeyboardButton('Help', callback_data='help')
                )
            keyboard.row(InlineKeyboardButton('Check Available Slots', callback_data='slots'))
            keyboard.row(InlineKeyboardButton('Bot Related Updates', url=f't.me/{config.BOT_OWNER}'))
            bot.send_message(
            message.chat.id,
            f'Welcome back <b>{username} !</b> \n\n' + config.HELP_TEXT + config.BOT_COMMANDS,
            reply_markup=keyboard)
            return None
        #if user not registered
        keyboard.row(
            InlineKeyboardButton('📘 Register', callback_data='register'),
            InlineKeyboardButton('Help', callback_data='help')
            )
        keyboard.row(InlineKeyboardButton('Bot Related Updates', url=f't.me/{config.BOT_OWNER}'))
        bot.send_message(
        message.chat.id,
        f'Hii <b>{username} !</b> Welcome to @{config.BOT_USERNAME} developed by @{config.BOT_OWNER}\n\n' + config.HELP_TEXT + config.BOT_COMMANDS,
        reply_markup=keyboard)
        with conn:
            username = '@' + str(message.chat.username) if message.chat.username else str(message.chat.first_name) if message.chat.first_name else str(message.chat.id)
            cur.execute(f"Insert into users (id, username, date) values ({message.chat.id}, '{username}', '{str(datetime.date.today())}')")
        return None
    except Exception as e:
        func.error_handler(e, func.whoami())
        
@bot.message_handler(chat_types=['private'], commands=['help'])
def help_command(message):
    try:
        if func.register_user(message):
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton('Report Bugs/Issues', callback_data='report-bug'),
                InlineKeyboardButton('Data & Policy', callback_data='policy')
                )
            keyboard.row(InlineKeyboardButton('Check Available Slots', callback_data='slots'))
            keyboard.row(InlineKeyboardButton('Bot Related Updates', url=f't.me/{config.BOT_OWNER}'))
            bot.send_message(
                message.chat.id,
                '<b>Help</b> \n\n' +
                config.HELP_TEXT + config.BOT_COMMANDS +
                'This bot is in <b>Beta</b> Phase, so if you find any bug or any problem in any of its Feature, Please provide feedback to the Developer by typing /reportbug to message to admin, admin will respond to your feedback as soon as possible. \n\n'
                f'Made with ❤️ by @{config.BOT_OWNER}',
                reply_markup=keyboard)
            return None
        help_command(message)
    except Exception as e:
        func.error_handler(e, func.whoami())

@bot.message_handler(chat_types=['private'], commands=['policy'])
def privacy_policy(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Delete Your Data', callback_data='delete-data'),
        InlineKeyboardButton('Report Bugs/Issues', callback_data='report-bug')
        )
    keyboard.row(InlineKeyboardButton('Bot Related Updates', url=f't.me/{config.BOT_OWNER}'))
    bot.send_message(
       message.chat.id,
       '<b>Data & Privacy</b> \n\n' +
       'We don\'t store any of your private data, we just use information which is necessary. This includes: \n' +
       f'• Telegram account user id ({message.chat.id}) (for notifications) \n\n' +
       '• The District Code / Pincode \n' +
       '• Age preference \n' +
       '• Vaccine preferences \n\n' +
       'The bot <b>does not have access</b> to your phone number. \n' +
       'Click on /delete to delete all your data.',
       reply_markup=keyboard
       )
        
@bot.message_handler(chat_types=['private'], commands=['reportbug'])
def report_bug(message):
    msg = bot.send_message(message.chat.id, 'Now write a message to send to the bot admin.\n\nYou can also attach screenshots or log file but all in single message or type /delete to cancel the operation')
    bot.register_next_step_handler(msg, process_report)

def edit_report(message, msg_txt):
    sender = '@' + str(message.chat.username) if message.chat.username else str(message.chat.first_name) if message.chat.first_name else 'User'
    return f'<b>{sender} ({message.chat.id}) :- </b>' + msg_txt

def process_report(message):
    try:
        if message.text == '/delete':
            bot.send_message(message.chat.id, 'Operation Cancelled')
            return None
        elif message.text[0] == '/':
            func.handle_cmd(message)
            return None
        send_to = config.LOG_GRP
        if message.content_type == 'text':
            bot.send_message(send_to, edit_report(message, message.html_text))
        elif message.content_type == 'video':
            bot.send_video(send_to, message.video.file_id, caption = edit_report(message, message.html_caption))
        elif message.content_type == 'photo':
            bot.send_photo(send_to, message.photo[len(message.photo) - 1].file_id, caption = edit_report(message, message.html_caption))
        elif message.content_type == 'document':
            bot.send_document(send_to, message.document.file_id, caption = edit_report(message, message.html_caption))
        else:
            bot.send_message(message.chat.id, 'This Message content is not supported for reporting Purpose.')
            return None
        bot.send_message(message.chat.id, 'Your Message is Sent to Admin 👍')
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
        
@bot.message_handler(commands=['gettodayslots', 'getweeklyslots'])
def send_slots(message):
    try:
        comp_detail = func.complete_detail(message)
        district_id, age, vaccine, fee_type, dose = comp_detail
        if message.text == '/gettodayslots':
            func.pull_daily_slots(message.chat.id, district_id, age, vaccine, fee_type, dose)
        else:
            func.pull_weekly_slots(message.chat.id, district_id, age, vaccine, fee_type, dose)
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
        
@bot.message_handler(commands=['getpincode', 'getpincodeweekly'])
def send_pincode_slots(message):
    # try:
    result = cur.execute(f"select pincode, age, vaccine, fee, dose from users where id = {message.chat.id}").fetchone()
    pincode, age, vaccine, fee_type, dose = result
    if message.text == '/getpincode':
        func.pull_daily_slots(message.chat.id, pincode, age, vaccine, fee_type, dose)
    else:
        func.pull_weekly_slots(message.chat.id, pincode, age, vaccine, fee_type, dose)
    # except Exception as e:
    #     func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
        
@bot.message_handler(chat_types=['private'], commands=['delete'])
def delete_user(message):
    try:
        result = cur.execute(f"Select * from users where id = {message.chat.id}").fetchone()
        if result:
            with conn:
                cur.execute(f"delete from users where id = {message.chat.id}")
            bot.send_message(message.chat.id, 'Your data Deleted Succesfully.')
        else:
            bot.send_message(message.chat.id, 'Your data is already Deleted by you.')
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
        
@bot.message_handler(chat_types=['private'], commands=['states'])
def add_states(message):
    try:
        if func.register_user(message):
            keyboard = InlineKeyboardMarkup()
            data = cowin.get_states()
            if not data:
                bot.send_message(message.chat.id, 'We are experiencing some issues please try again in a few moment or let developer know about it, use /reportbug')
                return None
            data = data.get('states')
            states = func.arrange_data_in_column(data)
            for state in states:
                try:
                    keyboard.row(
                        InlineKeyboardButton(state[0]["state_name"], callback_data=f'state-{state[0]["state_id"]}'),
                        InlineKeyboardButton(state[1]["state_name"], callback_data=f'state-{state[1]["state_id"]}')
                        )
                except:
                    keyboard.row(InlineKeyboardButton(state[0]["state_name"], callback_data=f'state-{state[0]["state_id"]}'))
                    bot.send_message(message.chat.id, 'Choose your state', reply_markup=keyboard)
            return None
        add_states(message)
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
    
def add_districts(message, state_id = None):
    try:
        bot.delete_message(message.chat.id, message.message_id)
        if state_id == None:
            add_states(message)
            return None
        keyboard = InlineKeyboardMarkup()
        data = cowin.get_districts(state_id).get('districts')
        districts = func.arrange_data_in_column(data)
        if districts:
            for district in districts:
                try:
                    keyboard.row(
                        InlineKeyboardButton(district[0]["district_name"], callback_data=f'district-{district[0]["district_id"]}'),
                        InlineKeyboardButton(district[1]["district_name"], callback_data=f'district-{district[1]["district_id"]}')
                        )
                except:
                    keyboard.row(InlineKeyboardButton(district[0]["district_name"], callback_data=f'district-{district[0]["district_id"]}'))
            bot.send_message(message.chat.id, 'Choose your District', reply_markup=keyboard)
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
        
@bot.message_handler(chat_types=['private'], commands=['age'])
def add_age(message):
    try:
        if func.register_user(message):
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton('15-17', callback_data='age-15'),
                InlineKeyboardButton('18 & above', callback_data='age-18')
            )
            bot.send_message(message.chat.id, 'Select your age preference :-', reply_markup=keyboard)
            return None
        add_age(message)
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
    
@bot.message_handler(chat_types=['private'], commands=['preferences'])
def add_preferences(message):
    try:
        if func.register_user(message):
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton('Covaxin', callback_data='vaccine-covaxin'),
                InlineKeyboardButton('Covishield', callback_data='vaccine-covishield'),
                InlineKeyboardButton('Sputnik V', callback_data='vaccine-sputnik v')
            )
            bot.send_message(message.chat.id, 'Select your Vaccine preference :-', reply_markup=keyboard)
            return None
        add_preferences(message)
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
    
@bot.message_handler(commands=['register'])
def user_registration(message):
    try:
        comp_detail = func.complete_detail(message)
        district_id, age, vaccine, fee_type, dose = comp_detail
        if age and district_id and vaccine and fee_type and dose:
            bot.send_message(message.chat.id, 'You have already Registered. Try /gettodayslots or /getweeklyslots to get Available slots according to your Preferences.')
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')

@bot.message_handler(commands=['pincode'])
def getPincode(message):
    try:
        result = cur.execute(f"Select pincode from users where id = {message.chat.id}").fetchone()[0]
        if result != 'None':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Update Pincode', callback_data='set-pincode'))
            bot.send_message(message.chat.id, f'Your Current Pincode is Set to {result}', reply_markup=keyboard)
        else:
            setPincode(message)
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
        
def setPincode(message):
    bot.send_message(message.chat.id, "Enter 6-digit Area Pincode :-")
    bot.set_state(message.chat.id, 4)
    
@bot.message_handler(state=4, is_digit=True)
def processPincode(message):
    try:
        pincode = message.text
        if len(pincode) != 6:
            processWrongPincode(message)
        else:
            with conn:
                cur.execute(f"update users set pincode = '{pincode}' where id = {message.chat.id}")
            bot.delete_state(message.chat.id)
            result = cur.execute(f"Select pincode from users where id = {message.chat.id}").fetchone()[0]
            if result != 'None':
                bot.send_message(message.chat.id, f'Done !! Your Pincode is set to {result}')
                func.complete_detail(message)
                return None
            bot.send_message(message.chat.id, 'Something went wrong Please try again !!')
            setPincode(message)
    except Exception as e:
        error_handler(e, f'{whoami()} ({os.path.basename(__file__)})')
    
@bot.message_handler(state=4, is_digit=False)
def processWrongPincode(message):
    bot.send_message(message.chat.id, "Please Enter Correct 6-digit Area Pincode :-")
        
@bot.message_handler(commands=['getotp'])
def getMobileOTP(message):
    bot.set_state(message.chat.id, 1)
    bot.send_message(message.chat.id, "Enter your 10-digit Mobile No.")

@bot.message_handler(state=1, is_digit=True)
def generateMobileOTP(message):
    with bot.retrieve_data(message.chat.id) as data:
        data['mobile'] = message.text
        mobile = data['mobile']
    data = {"mobile": mobile, "secret": Constants.secret_key}
    txnId = requests.post(url=Constants.otp_generate_url, json=data, headers=Constants.headers)
    if txnId.status_code == 200:
        bot.send_message(message.chat.id, f"Successfully requested OTP for mobile number {mobile} at {datetime.datetime.today()}..")
        txnId = txnId.json().get('txnId')
        bot.set_state(message.chat.id, 2)
        bot.send_message(message.chat.id, f'<b>Enter OTP sent on your mobile no. {mobile} :-</b>')
        with bot.retrieve_data(message.chat.id) as data:
            data['txnID'] = txnId
    else:
        bot.send_message(message.chat.id, f"<b>{txnId.status_code} Unable to Generate OTP</b> :- {txnId.text}")
        bot.send_message(message.chat.id, f"Retry with {mobile} ? (y/n Default y): ")
        
@bot.message_handler(state=2, is_digit=True)
def validateMobileOTP(message):
    otp = message.text
    with bot.retrieve_data(message.chat.id) as data:
        otp = sha256(otp.encode('utf-8')).hexdigest()
        json_data = {"otp": otp, "txnId": data['txnID']}
    bot.send_message(message.chat.id, "Validating OTP..")
    token = requests.post(url=Constants.download_cert, headers=Constants.headers, json=json_data)
    if token.status_code == 200:
        bot.delete_state(message.chat.id)
        token = token.json().get('token')
        with bot.retrieve_data(message.chat.id) as data:
            data['token'] = token
    else:
        bot.send_message(message.chat.id, f'<b>Unable to Validate OTP :- </b>{token.text}\n\nRetry again !!')
        
@bot.message_handler(commands=['getcertificate'])
def getVaccinationCertificate(message):
    try:
        with bot.retrieve_data(message.chat.id) as data:
            token = data.get('token')
        if not token:
            getMobileOTP(message)
            getVaccinationCertificate(message)
        else:
            bot.set_state(message.chat.id, 3)
            bot.send_message(message.chat.id, "Enter your Beneficiary Reference ID: ")
    except:
        getMobileOTP(message)
       
@bot.message_handler(state=3, is_digit=True) 
def handleBeneficiaryID(message):
    beneficiary_reference_id = message.text
    data = cowin.download_certificate(beneficiary_reference_id)
    print(data)
        
#handle callback query
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(query):
    try:
        bot.answer_callback_query(query.id)
        data = query.data
        if data.startswith('help'):
            help_command(query.message)
        elif data.startswith('policy'):
            privacy_policy(query.message)
        elif data.startswith('report-bug'):
            report_bug(query.message)
        elif data.startswith('users'):
            log.users_list(query.message)
        elif data.startswith('delete-data'):
            delete_user(query.message)
        elif data.startswith('register'):
            user_registration(query.message)
        elif data.startswith('preferences'):
            add_preferences(query.message)
        elif data.startswith('slots'):
            send_slots(query.message)
        elif data.startswith('age-'):
            func.process_age(query.message, query.data[4:])
        elif data.startswith('vaccine-'):
            func.process_vaccine(query.message, query.data[8:])
        elif data.startswith('fee-'):
            func.process_fee_type(query.message, query.data[4:])
        elif data.startswith('dose-'):
            func.process_dose(query.message, query.data[5:])
        elif data.startswith('state-'):
            add_districts(query.message, query.data[6:])
        elif data.startswith('district-'):
            func.process_district(query.message, query.data[9:])
        elif data.startswith('set-pincode'):
            bot.delete_message(query.message.chat.id, query.message.message_id)
            setPincode(query.message)
    except telebot.apihelper.ApiTelegramException as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
     
#Must be Last Command
@bot.message_handler(chat_types=['private'], func=lambda message: True, content_types=['text'])
def handle_msg(message):
    try:
        bot.reply_to(message, '<strong>Use Pre-defined Commands only !!</strong>')
    except Exception as e:
        func.error_handler(e, f'{func.whoami()} ({os.path.basename(__file__)})')
        
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())