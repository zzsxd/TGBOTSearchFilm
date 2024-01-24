#################################################
#                 created by                    #
#                     ZZS                       #
#                     SBR                       #
#################################################
import sqlite3
import os
import json
from kinopoisk import KPClient
from Frontend import Update_msg
import requests


class Parse_temp:
    def __init__(self, file):
        super(Parse_temp, self).__init__()
        self.__log_name = file
        self.__default_parsers = {'kinopoisk_unofficial': [0, []]}
        self.create()

    def create(self):
        if not os.path.exists(self.__log_name):
            self.write_log(self.__default_parsers)

    def get_parser_log(self, method):
        return self.read_log()[method]

    def update_parser_log(self, method, data):
        last_data = self.read_log()
        self.write_log(last_data.update({method: data}))

    def write_log(self, data):
        with open(self.__log_name, 'w') as file:
            json.dump(data, file, sort_keys=True, indent=4)

    def read_log(self):
        with open(self.__log_name, 'r') as file:
            return json.load(file)


class Parse_films:
    def __init__(self, bot_obj, chat_obj, kin_poisk_unofficial_api=None, start_id=None, end_id=None, db_obj=None, log_obj=None):
        super(Parse_films, self).__init__()
        self.__kin_poisk_apis = kin_poisk_unofficial_api
        self.__bot_obj = bot_obj
        self.__chat_obj = chat_obj
        self.__start_id = start_id
        self.__end_id = end_id
        self.__db_obj = db_obj
        self.__log_obj = log_obj
        self.__msg_obg = Update_msg()

    async def kin_unofficial_parser(self):
        success = 0
        error = 0
        count = 0
        for i in range(self.__start_id, self.__end_id):
            try:
                client = KPClient(self.__kin_poisk_apis[count // 500])
            except:
                count = i
                self.__log_obj.update_parser_log('kinopoisk_unofficial', [count])
                break
            try:
                film = await client.get_movie_data(i)
                photo = requests.get(film.poster.big).content
                self.__db_obj.db_write([film.name.ru, film.year, ', '.join(film.genres), film.raiting.kinopoisk.value,
                                        ', '.join(film.countries), f'{film.length} мин', film.description.long,
                                        film.url.kinopoisk, photo])
                success += 1
            except:
                error += 1
            finally:
                count += 1
        self.__msg_obg.send_msg_update(self.__bot_obj, self.__chat_obj, 12, addition=f'(Последняя попытка: {count}, Успешных загрузок: {success}, Загрузок с ошибкой: {error})')


class db_oper:
    def __init__(self, path):
        super(db_oper, self).__init__()
        self.__db_path = path
        self.cursor = None
        self.db = None
        self.init()

    def init(self):
        if not os.path.exists(self.__db_path):
            self.db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.cursor = self.db.cursor()
            self.cursor.execute('''CREATE TABLE films(
            name text,
            year text,
            janre text,
            rate text,
            country text,
            watchtime text,
            desc text,
            link text,
            cover BLOB
            )
            ''')
            self.db.commit()
        else:
            self.db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.cursor = self.db.cursor()

    def db_write(self, data):
        self.cursor.execute('INSERT INTO films VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
        self.db.commit()

    def db_read(self, data, mode):
        out = []
        years = []
        if mode == 'year' and '-' in data:
            years.extend(data.split('-'))
            self.cursor.execute(f'SELECT name, year, janre, rate, country, watchtime, desc, link, cover FROM films WHERE {mode} BETWEEN {years[0]} AND {years[1]} order by name')
        else:
            self.cursor.execute(f'SELECT name, year, janre, rate, country, watchtime, desc, link, cover FROM films WHERE {mode} LIKE "%{data}%" order by name')
        self.db.commit()
        for i in self.cursor.fetchall():
            out.append(i)
        if len(out) != 0:
            return out