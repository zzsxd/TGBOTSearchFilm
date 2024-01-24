#################################################
#                 created by                    #
#                     ZZS                       #
#                     SBR                       #
#################################################
from telebot import types
import copy

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

    def admin_buttons(self):
        btn1 = types.InlineKeyboardButton('Добавить фильм', callback_data='addfilm')
        btn2 = types.InlineKeyboardButton('Синхронизировать БД', callback_data="syncdb")
        btn3 = types.InlineKeyboardButton('Правка БД', callback_data='editdb')
        self.__markup.add(btn1, btn3, btn2)
        return self.__markup

    def developer_trebute(self):
        btn2 = types.InlineKeyboardButton('Донат', url='https://www.donationalerts.com/r/zzsnikita')
        btn3 = types.InlineKeyboardButton('Разработчики', callback_data='developers')
        self.__markup.add( btn2, btn3)
        return self.__markup

    def developers(self):
        btn1 = types.InlineKeyboardButton('zzsxd', url='https://github.com/zzsxd/')
        btn2 = types.InlineKeyboardButton('SBR', url='https://github.com/lifufkd')
        self.__markup.add(btn1, btn2)
        return self.__markup

class User_data:  ### взаимодействие со словарём состояний пользователей
    def __init__(self):
        super(User_data, self).__init__()
        self.__online_users = {}
        self.__default_admin = [True, False, 0, []]  ### [is_admin, update_db_now, update_index, current_action]

    def init(self, id, admins):  ### запускается только один раз при вводе /start
        default_user = [False, False, 0, [], None]
        if id not in self.__online_users.keys():
            if id in admins:
                default_user[0] = True
            self.__online_users.update({id: copy.deepcopy(default_user)})

    def get_players(self):
        return self.__online_users

    def update_pull(self, tg_id, data):
        self.__online_users[tg_id][3].append(data)

    def update_reset(self, tg_id):
        self.__online_users[tg_id][0:4] = copy.deepcopy(self.__default_admin)


class Update_msg:
    def __init__(self):
        super(Update_msg, self).__init__()
        self.__messages = ['Введите', 'название', 'год', 'жанр', 'рейтинг', 'страну', 'время просмотра', 'описание', 'ссылку', 'Отправьте обложку',
                           'Изменения успешно сохранены!', 'Завершите обновление!', 'Это не обложка!', 'Синхронизация завершена']

    def send_msg_update(self, bot_obj, chat_obj, stat, addition=None):
        if stat < 8:
            msg = f'{self.__messages[0]} {self.__messages[stat + 1]}'
        else:
            msg = f'{self.__messages[stat + 1]}'
        bot_obj.send_message(chat_obj, msg)


class Film_msg:
    def __init__(self):
        super(Film_msg, self).__init__()
        self.__messages = ['Введите', 'жанр фильма', 'год фильма', 'название фильма', 'Фильмы не найдены', 'Выберите действие✅']
        self.__msg_format = ['<b><i>Название</i></b>', '<b><i>Год</i></b>', '<b><i>Жанр</i></b>', '<b><i>Рейтинг</i></b>', '<b><i>Страна</i></b>', '<b><i>Время просмотра</i></b>', '<b><i>Описание</i></b>', '<b><i>Ссылка</i></b>']

    def send_msg_callback(self, bot_obj, chat_obj, stat):
        bot_obj.send_message(chat_id=chat_obj, text=f'{self.__messages[0]} {self.__messages[stat]}')

    def send_msg_handler(self, bot_obj, chat_obj, stat, markup_obj=None):
        if type(stat) is int:
            msg = self.__messages[stat]
        else:
            msg = stat
        bot_obj.send_message(chat_id=chat_obj, reply_markup=markup_obj, text=msg)

    def send_msg_photo(self, bot_obj, chat_obj, msg, photo, markup_obj=None):
        bot_obj.send_photo(chat_id=chat_obj, photo=photo, reply_markup=markup_obj, caption=msg, parse_mode='html')

    def get_messages(self):
        return self.__msg_format