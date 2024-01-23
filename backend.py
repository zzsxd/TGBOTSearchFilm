#################################################
#                 created by                    #
#                     ZZS                       #
#                     SBR                       #
#################################################
import sqlite3
import os

############static variables#####################
DB_path = 'db.sqlite3'
#################################################


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
            desc text,
            link text,
            rate text,
            country text,
            watchtime text,
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
            self.cursor.execute(f'SELECT name, year, janre, desc, link, rate, country, watchtime cover FROM films WHERE {mode} BETWEEN {years[0]} AND {years[1]} order by name')
        else:
            self.cursor.execute(f'SELECT name, year, janre, desc, link, rate, country, watchtime cover FROM films WHERE {mode} LIKE "%{data}%" order by name')
        self.db.commit()
        for i in self.cursor.fetchall():
            out.append(i)
        if len(out) != 0:
            return out