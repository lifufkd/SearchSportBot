#####################################
#            Created by             #
#               zzsxd               #
#               SBR                 #
#####################################
import os
import time
import shutil
import requests
from PIL import Image
from datetime import datetime
import pandas as pd
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, [], [], [], None]})
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

    def clean_db(self):
        self.__db.db_write('DELETE FROM basketball', ())
        self.__db.db_write('DELETE FROM football', ())
        self.__db.db_write('DELETE FROM hockey', ())

    def get_team_matches(self, sport, team):
        result = list()
        data = self.__db.db_read(f'SELECT `date`, `first_team`, `second_team` FROM "{sport}" ORDER BY `date` ASC', ())
        for element in data:
            if len(result) >= 5:
                break
            elif (team.lower() in element[1].lower() or team.lower() in element[2].lower()) and datetime.strptime(element[0], "%Y-%m-%d %H:%M:%S") > datetime.now():
                result.append(element)
        return result


class BuildPhoto:
    def __init__(self, logo1, logo2, sport):
        super(BuildPhoto, self).__init__()
        self.__logo1_link = logo1
        self.__logo2_link = logo2
        self.prepare_links()
        self.download_image(sport, self.__logo1_link, f'img/temp/{sport}/logo1.png')
        self.download_image(sport, self.__logo2_link, f'img/temp/{sport}/logo2.png')
        background_image = self.choose_background(sport)
        self.build(f'img/temp/{sport}/logo1.png', f'img/temp/{sport}/logo2.png', background_image, sport)

    def prepare_links(self):
        self.__logo1_link = self.__logo1_link.replace('small', 'big')
        self.__logo2_link = self.__logo2_link.replace('small', 'big')

    def choose_background(self, sport):
        match sport:
            case 'football':
                return 'img/background_football.jpg'
            case 'basketball':
                return 'img/background_basketball.jpg'
            case 'hockey':
                return 'img/background_hockey.jpg'

    def download_image(self, sport, link, path):
        response = requests.get(link)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
        else:
            shutil.copyfile(f'img/{sport}/no.png', path)
        img = Image.open(path)
        new_image = img.resize((100, 100))
        new_image.save(path)

    def build(self, logo1, logo2, background_image, sport):
        logo1 = Image.open(logo1)
        logo2 = Image.open(logo2)
        background_image = Image.open(background_image)
        logo1_width, logo1_height = logo1.size
        logo2_width, logo2_height = logo2.size
        padding = 50
        combined_width = logo1_width + padding + logo2_width
        combined_height = max(logo1_height, logo2_height)
        combined_image = Image.new("RGBA", (combined_width, combined_height), (255, 255, 255, 0))
        combined_image.paste(logo1, (0, (combined_height - logo1_height) // 2))
        combined_image.paste(logo2, (logo1_width + padding, (combined_height - logo2_height) // 2))
        background_image = background_image.resize((combined_width, combined_height))
        combined_image = Image.alpha_composite(background_image.convert('RGBA'), combined_image)
        combined_image.save(f'img/temp/{sport}/result.png')
