from cowin import bot

if __name__ == '__main__':
	bot.remove_webhook()
	bot.polling(skip_pending=True)

	#Use Infinity Polling in case you don't wanna bot to be stopped on any error/exception
	# bot.infinity_polling(skip_pending=True)