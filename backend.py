#####################################
#            Created by             #
#               zzsxd               #
#               SBR                 #
#####################################
import os
import time
import pandas as pd
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, [], [], []]})
        return self.__user_data


class DbAct:
    def __init__(self, db, config, path_xlsx):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__fields = ['Имя', 'Фамилия', 'Никнейм']
        self.__dump_path_xlsx = path_xlsx

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write(
                'INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin) VALUES (?, ?, ?, ?, ?)',
                (user_id, first_name, last_name, nick_name, is_admin))

    def user_is_existed(self, user_id):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def user_is_admin(self, user_id):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def update_sport(self, sport, data):
        self.__db.db_write(f'INSERT INTO "{sport}" (date, first_team, second_team) VALUES(?, ?, ?)', data)

    def last_sport_date(self, sport):
        return self.__db.db_read(f'SELECT MAX(date) FROM "{sport}"', ())[0][0]

    def get_team_matches(self, sport, team):
        return self.__db.db_read(f'SELECT date, first_team, second_team FROM "{sport}" WHERE first_team LIKE lower("%{team}%") OR second_team LIKE lower("%{team}%") ORDER BY date ASC LIMIT 5 COLLATE NOCASE', ())

    def get_team_matches_strict(self, sport, team):
        return self.__db.db_read(f'SELECT date, first_team, second_team FROM "{sport}" WHERE first_team = "{team}" OR second_team = "{team}" ORDER BY date ASC LIMIT 5', ())


    def db_export_xlsx(self):
        d = {'Имя': [], 'Фамилия': [], 'Никнейм': []}
        users = self.__db.db_read('SELECT first_name, last_name, nick_name FROM users', ())
        if len(users) > 0:
            for user in users:
                for info in range(len(list(user))):
                    d[self.__fields[info]].append(user[info])
            df = pd.DataFrame(d)
            df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='пользователи', index=False)
