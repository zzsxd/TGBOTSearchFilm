#################################################
#                 created by                    #
#                     ZZS                       #
#                     SBR                       #
#################################################
import telebot
from telebot import types
from backend import db_oper

############static variables#####################
TG_api = '6723388582:AAFgzZfo9KG-UE8ZDKkxsyylwLJMAkEXms4'
admins = [818895144], [1897256227]
#################################################

bot = telebot.TeleBot(TG_api)


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=2)

    def start_btns(self):
        btn1 = types.InlineKeyboardButton('Жанры', callback_data='genre')
        btn2 = types.InlineKeyboardButton('Года', callback_data='years')
        btn3 = types.InlineKeyboardButton('Поиск по названию', callback_data='name')
        self.__markup.add(btn1, btn2, btn3)
        return self.__markup

    def creators_btns(self):
        btn1 = types.InlineKeyboardButton('Жанры', callback_data='genre')
        btn2 = types.InlineKeyboardButton('Года', callback_data='years')
        btn3 = types.InlineKeyboardButton('Поиск по названию', callback_data='name')
        self.__markup.add(btn1, btn2, btn3)
        return self.__markup


class User_data:  ### взаимодействие со словарём состояний пользователей
    def __init__(self):
        super(User_data, self).__init__()
        self.__online_users = {}
        self.__default_admin = [True, False, 0, []]  ### [is_admin, update_db_now, update_index]

    def init(self, id):  ### запускается только один раз при вводе /start
        default_user = [False, False, 0, []]
        if id not in self.__online_users.keys():
            if id in admins:
                default_user[0] = True
            self.__online_users.update({id: default_user})

    def get_players(self):
        return self.__online_users

    def update_pull(self, id, data):
        self.__online_users[id][3].append(data)

    def update_reset(self, id):
        self.__online_users[id][3].clear()
        self.__online_users[id][0:4] = self.__default_admin


class Add_new_entry:
    def __init__(self):
        super(Add_new_entry, self).__init__()
        self.__massages = ['Введите', 'название', 'год', 'жанр', 'описание', 'ссылку', 'Отправьте обложку',
                           'Изменения успешно сохранены!', 'Завершите обновление!', 'Это не обложка!']

    def send_msg_update(self, bot_obj, chat_obj, stat):
        if stat < 5:
            msg = f'{self.__massages[0]} {self.__massages[stat + 1]}'
        else:
            msg = f'{self.__massages[stat + 1]}'
        bot_obj.send_message(chat_obj, msg)


@bot.message_handler(commands=['start', 'creators', 'update'])
def start(message):
    command = message.text.replace('/', '')
    user_ID = message.from_user.id
    user.init(user_ID)
    send = Add_new_entry()
    if not user.get_players()[user_ID][1]:
        if command == 'start':
            buttons = Bot_inline_btns()
            bot.reply_to(message,
                         'Привет👋\nЯ SearchFilmBot🤖 - помогу с поиском интересного фильма!\nНапишите /creators для получения информации о создателях.')
            bot.send_message(message.chat.id, 'Выберите действие✅', reply_markup=buttons.start_btns())
        elif command == 'creators':
            buttons = Bot_inline_btns()
            bot.reply_to(message, 'Создатели:\nzzsxd - фронтенд составляющая бота.\nSBR - бэкенд составляющая бота.')
            bot.send_message(message.chat.id, 'Выберите действие✅', reply_markup=buttons.creators_btns())
        elif command == 'update' and user.get_players()[user_ID][0]:
            send.send_msg_update(bot, message.chat.id, user.get_players()[user_ID][2])
            user.get_players()[user_ID][1] = True
    else:
        send.send_msg_update(bot, message.chat.id, 7)


@bot.message_handler(content_types=['photo', 'video', 'voice', 'audio', 'image', 'sticker', 'text'])
def text(message):
    user_ID = message.from_user.id
    send = Add_new_entry()
    if user_ID in user.get_players():
        if message.text is None and user.get_players()[user_ID][2] != 5:
            bot.reply_to(message, '🚫Ошибка: неверный формат ввода🚫')
        else:
            if user.get_players()[user_ID][0] and user.get_players()[user_ID][1]:
                if user.get_players()[user_ID][2] == 5 and message.text is None:  ### последний этап обновления БД
                    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                    downloaded_file = bot.download_file(file_info.file_path)  ### загрузка обложки
                    user.update_pull(user_ID,
                                     downloaded_file)  ### добавление обложки в массив для добавление новой записи в БД
                    db.db_write(user.get_players()[user_ID][3])  ### запись в БД
                    user.update_reset(user_ID)  ### очистка массива
                    send.send_msg_update(bot, message.chat.id, 6)
                elif user.get_players()[user_ID][2] == 5:  ## обработка ошибки при отправке не фото
                    send.send_msg_update(bot, message.chat.id, 8)
                else:
                    user.update_pull(user_ID, message.text)  ### обновление массива
                    user.get_players()[user_ID][2] += 1  ### счётчик этапа
                    send.send_msg_update(bot, message.chat.id, user.get_players()[user_ID][
                        2])  ### отправка сообщения пользователю что ему вводить


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'genre':
        print('Пользователь нажал кнопку: "Жанры"')
        msg = bot.send_message(call.message.chat.id, 'Введите жанр фильма')

        @bot.message_handler(content_types=['text'])
        def handle_text_message(message):
            if message.chat.id == call.message.chat.id:  # Проверяем, что сообщение отправлено в тот же чат, что и исходное нажатие кнопки
                mode = 'genre'
                result = db.db_read(message.text, mode)
                if result:
                    for film in result:
                        msg = ''
                        for i, item in enumerate(film):
                            if i != 0:
                                msg += f'{item}\n'
                        bot.send_message(chat_id=call.message.chat.id, text=msg)
                    bot.send_message(chat_id=call.message.chat.id, text='Выберите действие',
                                     reply_markup=Bot_inline_btns().start_btns())
                else:
                    bot.send_message(chat_id=call.message.chat.id, text='Фильмы не найдены')

        bot.register_next_step_handler(msg, handle_text_message)


    elif call.data == 'years':
        print('Пользователь нажал кнопку: "Года"')
        msg = bot.send_message(call.message.chat.id, 'Введите год фильма')

        @bot.message_handler(content_types=['text'])
        def handle_text_message(message):
            global msg
            if message.chat.id == call.message.chat.id:  # Проверяем, что сообщение отправлено в тот же чат, что и исходное нажатие кнопки
                mode = 'years'
                result = db.db_read(message.text, mode)
                if result:
                    for film in result:
                        msg = ''
                        for i, item in enumerate(film):
                            if i != 0:
                                msg += f'{item}\n'
                        bot.send_message(chat_id=call.message.chat.id, text=msg)
                    bot.send_message(chat_id=call.message.chat.id, text='Выберите действие',
                                     reply_markup=Bot_inline_btns().start_btns())
                else:
                    bot.send_message(chat_id=call.message.chat.id, text='Фильмы не найдены')
            bot.register_next_step_handler(msg, handle_text_message)


    elif call.data == 'name':
        print('Пользователь нажал кнопку: "Поиск по названию"')
        msg = bot.send_message(call.message.chat.id, 'Введите название фильма')

        @bot.message_handler(content_types=['text'])
        def handle_text_message(message):
            global msg
            if message.chat.id == call.message.chat.id:  # Проверяем, что сообщение отправлено в тот же чат, что и исходное нажатие кнопки
                mode = 'name'
                result = db.db_read(message.text, mode)
                if result:
                    for film in result:
                        msg = ''
                        for i, item in enumerate(film):
                            if i != 0:
                                msg += f'{item}\n'
                        bot.send_message(chat_id=call.message.chat.id, text=msg)
                    bot.send_message(chat_id=call.message.chat.id, text='Выберите действие',
                                     reply_markup=Bot_inline_btns().start_btns())
                else:
                    bot.send_message(chat_id=call.message.chat.id, text='Фильмы не найдены')
            bot.register_next_step_handler(msg, handle_text_message)


user = User_data()
db = db_oper()

bot.polling(none_stop=True)

#   вообщем, в callback для каждого метода добавь вызов функции db.db_read(data, mode)
#   data - сообщение пользователя, mode - это режим т.е жанр, год и т.д
#   эта функция в случае наличия вернёт 2D массив (прочитай что это)
#   в цикле для этого 2D массива выводи отдельное сообщение (одно повторение цикла - один фильм)
#   в этом массиве есть фотография (обложка) найди способ добавить его в одно и то же сообшение
