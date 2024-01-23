#################################################
#                 created by                    #
#                     ZZS                       #
#                     SBR                       #
#################################################
import sqlite3
import os
from kinopoisk import KPClient
from Frontend import Update_msg
import requests

############static variables#####################
DB_path = 'db.sqlite3'
#################################################


class Parse_films:
    def __init__(self, bot_obj, chat_obj, kin_poisk_unofficial_api=None, start_id=None, end_id=None):
        super(Parse_films, self).__init__()
        self.__kin_poisk_apis = kin_poisk_unofficial_api
        self.__bot_obj = bot_obj
        self.__chat_obj = chat_obj
        self.__start_id = start_id
        self.__end_id = end_id
        self.__db_obj = db_oper()
        self.__msg_obg = Update_msg()

    async def kin_unofficial_parser(self):
        success = 0
        error = 0
        count = 0
        i = 0
        try:
            for i in range(self.__start_id, self.__end_id):
                client = KPClient(self.__kin_poisk_apis[count // 500])
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
        ##self.__msg_obg.send_msg_update(self.__bot_obj, self.__chat_obj, 12, addition=f'(Last attempt: {i}, Success downloads: {success}, Error downloads: {error})') хуй знает как сделать


class db_oper:
    def __init__(self):
        super(db_oper, self).__init__()
        self.cursor = None
        self.db = None
        self.init()

    def init(self):
        if not os.path.exists(DB_path):
            self.db = sqlite3.connect(DB_path, check_same_thread=False)
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
            self.db = sqlite3.connect(DB_path, check_same_thread=False)
            self.cursor = self.db.cursor()

    def db_write(self, data):
        self.cursor.execute('INSERT INTO films VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
        self.db.commit()

    def db_read(self, data, mode):
        out = []
        years = []
        if mode == 'year' and '-' in data:
            years.extend(data.split('-'))
            print(mode, years)
            self.cursor.execute(f'SELECT name, year, janre, rate, country, watchtime, desc, link, cover FROM films WHERE {mode} BETWEEN {years[0]} AND {years[1]} order by name')
        else:
            self.cursor.execute(f'SELECT name, year, janre, rate, country, watchtime, desc, link, cover FROM films WHERE {mode} LIKE "%{data}%" order by name')
        self.db.commit()
        for i in self.cursor.fetchall():
            out.append(i)
        if len(out) != 0:
            return out