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
admins = [818895144, 1897256227]
#################################################

bot = telebot.TeleBot(TG_api)


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=2)

    def start_btns(self):
        btn1 = types.InlineKeyboardButton('Жанры', callback_data='janre')
        btn2 = types.InlineKeyboardButton('Года', callback_data='year')
        btn3 = types.InlineKeyboardButton('Поиск по названию', callback_data='name')
        self.__markup.add(btn1, btn2, btn3)
        return self.__markup

    def creators_btns(self):
        btn1 = types.InlineKeyboardButton('Жанры', callback_data='janre')
        btn2 = types.InlineKeyboardButton('Года', callback_data='year')
        btn3 = types.InlineKeyboardButton('Поиск по названию', callback_data='name')
        self.__markup.add(btn1, btn2, btn3)
        return self.__markup


class User_data:  ### взаимодействие со словарём состояний пользователей
    def __init__(self):
        super(User_data, self).__init__()
        self.__online_users = {}
        self.__default_admin = [True, False, 0, [], None]  ### [is_admin, update_db_now, update_index, current_action]

    def init(self, id):  ### запускается только один раз при вводе /start
        default_user = [False, False, 0, [], None]
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


class Update_msg:
    def __init__(self):
        super(Update_msg, self).__init__()
        self.__messages = ['Введите', 'название', 'год', 'жанр', 'описание', 'ссылку', 'рейтинг', 'страну', 'время просмотра', 'Отправьте обложку',
                           'Изменения успешно сохранены!', 'Завершите обновление!', 'Это не обложка!']

    def send_msg_update(self, bot_obj, chat_obj, stat):
        if stat < 8:
            msg = f'{self.__messages[0]} {self.__messages[stat + 1]}'
        else:
            msg = f'{self.__messages[stat + 1]}'
        bot_obj.send_message(chat_obj, msg)


class Film_msg:
    def __init__(self):
        super(Film_msg, self).__init__()
        self.__messages = ['Введите', 'жанр фильма', 'год фильма', 'название фильма', 'Фильмы не найдены', 'Выберите действие✅']
        self.__msg_format = ['Название', 'Год', 'Жанр', 'Рейтинг', 'Страна', 'Время просмотра', 'Описание', 'Ссылка']

    def send_msg_callback(self, bot_obj, chat_obj, stat):
        bot_obj.send_message(chat_id=chat_obj, text=f'{self.__messages[0]} {self.__messages[stat]}')

    def send_msg_handler(self, bot_obj, chat_obj, stat, markup_obj=None):
        if type(stat) is int:
            msg = self.__messages[stat]
        else:
            msg = stat
        bot_obj.send_message(chat_id=chat_obj, reply_markup=markup_obj, text=msg)

    def send_msg_photo(self, bot_obj, chat_obj, msg, photo, markup_obj=None):
        bot_obj.send_photo(chat_id=chat_obj, photo=photo, reply_markup=markup_obj, caption=msg)

    def get_messages(self):
        return self.__msg_format


@bot.message_handler(commands=['start', 'creators', 'update'])
def start(message):
    command = message.text.replace('/', '')
    user_ID = message.from_user.id
    user.init(user_ID)
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
        elif command == 'update' and user.get_players()[user_ID][0]:
            send.send_msg_update(bot, message.chat.id, user.get_players()[user_ID][2])
            user.get_players()[user_ID][1] = True
    else:
        send.send_msg_update(bot, message.chat.id, 11)


@bot.message_handler(content_types=['photo', 'video', 'voice', 'audio', 'image', 'sticker', 'text'])
def text(message):
    user_ID = message.from_user.id
    send_update = Update_msg()
    send_get = Film_msg()
    buttons = Bot_inline_btns()
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
                    send_update.send_msg_update(bot, message.chat.id, 6)
                elif user.get_players()[user_ID][2] == 5:  ## обработка ошибки при отправке не фото
                    send_update.send_msg_update(bot, message.chat.id, 8)
                else:
                    user.update_pull(user_ID, message.text)  ### обновление массива
                    user.get_players()[user_ID][2] += 1  ### счётчик этапа
                    send_update.send_msg_update(bot, message.chat.id, user.get_players()[user_ID][
                        2])  ### отправка сообщения пользователю что ему вводить
            elif user.get_players()[user_ID][4] is not None:
                query = db.db_read(message.text, user.get_players()[user_ID][4])
                if query is not None:
                    for film in query:
                        msg = ''
                        photo = b''
                        for line in range(len(film)):
                            if line < 5:
                                msg += f'{send_get.get_messages()[line]}: {film[line]}\n'
                            else:
                                photo = film[line]
                        send_get.send_msg_photo(bot, message.chat.id, msg, photo)
                    user.get_players()[user_ID][4] = None
                    send_get.send_msg_handler(bot, message.chat.id, 5, buttons.start_btns())
                else:
                    send_get.send_msg_handler(bot, message.chat.id, 4)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    send = Film_msg()
    user_ID = call.message.chat.id
    user.get_players()[user_ID][4] = call.data
    if call.data == 'janre':
        send.send_msg_callback(bot, call.message.chat.id, 1)
    elif call.data == 'year':
        send.send_msg_callback(bot, call.message.chat.id, 2)
    elif call.data == 'name':
        send.send_msg_callback(bot, call.message.chat.id, 3)


user = User_data()
db = db_oper()

bot.polling(none_stop=True)

#   осталось сделать гиперссылку и прикрепить фото обложки к сообщению
