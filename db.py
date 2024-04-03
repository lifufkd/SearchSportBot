#####################################
#            Created by             #
#               zzsxd               #
#####################################
import os
import sqlite3
#####################################


class DB:
    def __init__(self, path, lock):
        super(DB, self).__init__()
        self.__lock = lock
        self.__db_path = path
        self.__cursor = None
        self.__db = None
        self.init()

    def sqlite_lower(self, value_):
        return value_.lower()

        # Переопределение функции преобразования к верхнему геристру

    def sqlite_upper(self, value_):
        return value_.upper()

    # Переопределение правила сравнения строк
    def ignore_case_collation(self, value1_, value2_):
        if value1_.lower() == value2_.lower():
            return 0
        elif value1_.lower() < value2_.lower():
            return -1
        else:
            return 1

    def init(self):
        if not os.path.exists(self.__db_path):
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()
            self.__cursor.execute('''
            CREATE TABLE users(
            row_id INTEGER primary key autoincrement not null,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            nick_name TEXT,
            is_admin BOOL,
            UNIQUE(user_id)
            )
            ''')
            self.__cursor.execute('''
                        CREATE TABLE football(
                        row_id INTEGER primary key autoincrement not null,
                        date DATE,
                        first_team TEXT,
                        second_team TEXT
                        )
                        ''')
            self.__cursor.execute('''
                                    CREATE TABLE hockey(
                                    row_id INTEGER primary key autoincrement not null,
                                    date DATE,
                                    first_team TEXT,
                                    second_team TEXT
                                    )
                                    ''')
            self.__cursor.execute('''
                                    CREATE TABLE basketball(
                                    row_id INTEGER primary key autoincrement not null,
                                    date DATE,
                                    first_team TEXT,
                                    second_team TEXT
                                    )
                                    ''')
            self.__db.commit()
        else:
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__db.create_collation("NOCASE", self.ignore_case_collation)
            self.__cursor = self.__db.cursor()

    def db_write(self, queri, args):
        with self.__lock:
            self.__cursor.execute(queri, args)
            self.__db.commit()

    def db_read(self, queri, args):
        with self.__lock:
            self.__cursor.execute(queri, args)
            return self.__cursor.fetchall()

    def set_lock(self):
        self.__lock.acquire(True)

    def realise_lock(self):
        self.__lock.release()