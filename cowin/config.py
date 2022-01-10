BOT_TOKEN = '' #Your Bot Token
BOT_NAME = '' #Bot Name
BOT_USERNAME = '' #Bot Username with @
BOT_OWNER = '' #Bot official Channel or Bots owner ID
TIMEZONE = 'Asia/Kolkata'
ADMINS_LIST_DICT = {'' : '@'} #chat id : username of admin
SOURCE_CODE = r'https://github.com/itsydv/CoWin'

BOT_COMMANDS = '<b>Available commands :</b>\n' + '/start - Initialize the bot \n' + '/help - Bots commands and How It works \n' + '/policy - Bot\'s data usage and Privacy Policy \n' + '/register - To register yourself by giving some minimal informations\n' + '/delete - Delete all your data from Bot including age, vaccine preferences\n' + '/gettodayslots - To get todays available vaccine slots\n' + '/getweeklyslots - To get weekly available vaccine slots\n' + '/pincode - To set your Area Pincode\n' + '/getpincode - To get todays available vaccine slots Using PINCODE\n' + '/getpincodeweekly - To get weekly available vaccine slots by using PINCODE\n' + '/states - To set your state and district\n' + '/age - To set age preferences\n' + '/preferences - To set vaccine preferences\n' + '/reportbug - Send a message to the bot Admin\n' + '\n'
HELP_TEXT = 'I will help you in Finding Available slots for Vaccine in your area and display results to you. To start, click on "Check Available Slots". For first time users, first Register yourself with us by clicking 📘 Register. \n\nTo get the slots Information type /gettodayslots or /getweeklyslots.\n'

#Logging Details
LOG_GRP = '' #chat id of ur personal grp where you wannna recieve bot logs and add bot to that grp
DB_FILE = 'users.db'

#Hosting Details
HOST_USERNAME = '' #pythonanywhere username of webpage
SECRET_KEY = '' #any random secret key

class Constants:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
        'origin': 'https://selfregistration.cowin.gov.in/',
        'referer': 'https://selfregistration.cowin.gov.in/'
        }
    
    secret_key = "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw=="
    
    base_url = "https://cdn-api.co-vin.in/api/v2" #production level
    # base_url = "https://cdndemo-api.co-vin.in/api/v2" #development level
    
    otp_generate_url = f"{base_url}/auth/generateMobileOTP"
    otp_confirm_url = f"{base_url}/auth/public/confirmOTP"

    states_list = f"{base_url}/admin/location/states"
    districts_list = f"{base_url}/admin/location/districts"

    availability_by_pincode = f"{base_url}/appointment/sessions/public/findByPin"
    availability_by_pincode_week = f"{base_url}/appointment/sessions/public/calendarByPin"
    availability_by_district = f"{base_url}/appointment/sessions/public/findByDistrict"
    availability_by_district_week = f"{base_url}/appointment/sessions/public/calendarByDistrict"
    
    download_cert = f"{base_url}/registration/certificate/public/download"

    DD_MM_YYYY = "%d-%m-%y"