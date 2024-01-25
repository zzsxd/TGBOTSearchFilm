#################################################
#                 created by                    #
#                     ZZS                       #
#                     SBR                       #
#################################################
import telebot
import asyncio
import json
from backend import db_oper, Parse_films, Parse_temp
from Frontend import Bot_inline_btns, Update_msg, User_data, Film_msg

############static variables#####################
TG_api = '6723388582:AAFgzZfo9KG-UE8ZDKkxsyylwLJMAkEXms4'
parse_temp_file = 'parser.txt'
DB_path = 'db.sqlite3'
admins = [818895144, 1897256227]
#################################################

bot = telebot.TeleBot(TG_api)


@bot.message_handler(commands=['start', 'creators', 'admin'])
def start(message):
    command = message.text.replace('/', '')
    user_ID = message.from_user.id
    user.init(user_ID, admins)
    send = Update_msg()
    buttons = Bot_inline_btns()
    if not user.get_players()[user_ID][1]:
        if command == 'start':
            bot.reply_to(message,
                         'Привет👋\nЯ SearchFilmBot🤖 - помогу с поиском интересного фильма!\nНапишите /creators для получения информации о создателях.')
            bot.send_message(message.chat.id, 'Выберите действие✅', reply_markup=buttons.start_btns())
        elif command == 'creators':
            bot.reply_to(message, 'Создатели:\nzzsxd - фронтенд составляющая бота.\nSBR - бэкенд составляющая бота.')
            bot.send_message(message.chat.id, 'Выберите действие✅', reply_markup=buttons.creators_btns())
        elif command == 'admin' and user.get_players()[user_ID][0]:
            bot.reply_to(message, f'Приветствую, {message.from_user.first_name}')
            bot.send_message(message.chat.id, 'Выбери действие✅', reply_markup=buttons.admin_buttons())
    else:
        send.send_msg_update(bot, message.chat.id, 10)


@bot.message_handler(content_types=['photo', 'video', 'voice', 'audio', 'image', 'sticker', 'text'])
def text(message):
    user_ID = message.from_user.id
    if user_ID in user.get_players():
        send_update = Update_msg()
        send_get = Film_msg()
        buttons = Bot_inline_btns()
        if message.text is None and user.get_players()[user_ID][2] != 8:
            bot.reply_to(message, '🚫Ошибка: неверный формат ввода🚫')
        else:
            if user.get_players()[user_ID][0] and user.get_players()[user_ID][1]:
                if user.get_players()[user_ID][2] == 8 and message.text is None:  ### последний этап обновления БД
                    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                    downloaded_file = bot.download_file(file_info.file_path)  ### загрузка обложки
                    user.update_pull(user_ID,
                                     downloaded_file)  ### добавление обложки в массив для добавление новой записи в БД
                    db.db_write(user.get_players()[user_ID][3])  ### запись в БД
                    user.update_reset(user_ID)  ### очистка массива
                    send_update.send_msg_update(bot, message.chat.id, 9)
                elif user.get_players()[user_ID][2] == 8:  ## обработка ошибки при отправке не фото
                    send_update.send_msg_update(bot, message.chat.id, 11)
                else:
                    user.update_pull(user_ID, message.text)  ### обновление массива
                    user.get_players()[user_ID][2] += 1  ### счётчик этапа
                    send_update.send_msg_update(bot, message.chat.id, user.get_players()[user_ID][
                        2])  ### отправка сообщения пользователю что ему вводить
            elif user.get_players()[user_ID][4] in ['janre', 'year', 'name']:
                query = db.db_read(message.text, user.get_players()[user_ID][4])
                if query is not None:
                    for film in query:
                        msg = ''
                        photo = b''
                        for line in range(len(film)):
                            if line < 8:
                                msg += f'{send_get.get_messages()[line]}: {film[line]}\n'
                            else:
                                photo = film[line]
                        send_get.send_msg_photo(bot, message.chat.id, msg, photo)
                    user.get_players()[user_ID][4] = None
                    send_get.send_msg_handler(bot, message.chat.id, 5, buttons.developer_trebute())
                else:
                    send_get.send_msg_handler(bot, message.chat.id, 4)
            elif user.get_players()[user_ID][4] == 'syncdb':
                log = Parse_temp(parse_temp_file)
                data = log.get_parser_log('kinopoisk_unofficial')
                apis = message.text.split(',')
                if apis != ['*'] or len(data[1]) != 0:
                    if apis != ['*']:
                        log.update_parser_log('kinopoisk_unofficial', [data[0], apis])
                    else:
                        apis = data[1]
                    bot.send_message(message.chat.id, 'Процесс обновления запущен')
                    parser = Parse_films(bot, message.chat.id,
                                         db_obj=db,
                                         log_obj=log,
                                         kin_poisk_unofficial_api=apis,
                                         start_id=data[0],
                                         end_id=99999999)
                    asyncio.run(parser.kin_unofficial_parser())
                else:
                    bot.send_message(message.chat.id, 'Ключи не введены!')
    else:
        bot.send_message(message.chat.id, '🚫Ошибка. Введите /start, чтобы запустить бота🚫')

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_ID = call.message.chat.id
    buttons = Bot_inline_btns()
    if user_ID in user.get_players():
        send_msg = Update_msg()
        send = Film_msg()
        user.get_players()[user_ID][4] = call.data
        if call.data == 'janre':
            send.send_msg_callback(bot, call.message.chat.id, 1)
        elif call.data == 'year':
            send.send_msg_callback(bot, call.message.chat.id, 2)
        elif call.data == 'name':
            send.send_msg_callback(bot, call.message.chat.id, 3)
        elif call.data == 'addfilm':
            send_msg.send_msg_update(bot, call.message.chat.id, user.get_players()[user_ID][2])
            user.get_players()[user_ID][1] = True
        elif call.data == 'syncdb':
            bot.send_message(call.message.chat.id, 'Введите API ключ(-и) kinopoisk_unofficial в формате *,*. Укажите "*" для использования сохраненных ключей')
        elif call.data == 'editdb':
            pass
        elif call.data == 'developers':
            bot.send_message(call.message.chat.id, 'Разработчики', reply_markup=buttons.developers())
    else:
        bot.send_message(call.message.chat.id, '🚫Ошибка. Введите /start, чтобы запустить бота🚫')


user = User_data()
db = db_oper(DB_path)

bot.polling(none_stop=True)

#   осталось сделать гиперссылку и прикрепить фото обложки к сообщению
