import telebot

bot = telebot.TeleBot('')

bot.polling(none_stop=True)