#####################################
#            Created by             #
#               zzsxd               #
#               SBR                 #
#####################################
import json
import os
import undetected_chromedriver as uc
import time
import sys
from datetime import datetime
from selenium.webdriver.common.by import By
#####################################


class ConfigParser:
    def __init__(self, file_path, os_type):
        super(ConfigParser, self).__init__()
        self.__file_path = file_path
        self.__default_pathes = {'Windows': 'C:\\', 'Linux': '/'}
        self.__default = {'tg_api': '', 'admins': [], 'db_file_name': '', 'FAQ': '', 'contacts': '', 'start_msg': '', 'step_sale': 500, 'percent_sale': 0, 'terminal_key': '', 'terminal_password': '', 'token': ''}
        self.__current_config = None
        self.load_conf()

    def load_conf(self):
        if os.path.exists(self.__file_path):
            with open(self.__file_path, 'r', encoding='utf-8') as file:
                self.__current_config = json.loads(file.read())
            if len(self.__current_config['tg_api']) == 0:
                sys.exit('config is invalid')
        else:
            self.create_conf(self.__default)
            sys.exit('config is not existed')

    def create_conf(self, config):
        with open(self.__file_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(config, sort_keys=True, indent=4))

    def get_config(self):
        return self.__current_config


class AllMatches:
    def __init__(self):
        super(AllMatches, self).__init__()
        self.__month = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
                 'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
        self.__driver = None
        self.__input_field = None

    def init(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless=new")  # for Chrome >= 109
        self.__driver = uc.Chrome()

    def first_phase(self, name):
        self.__driver.get('https://www.ligastavok.ru/')
        time.sleep(5)
        self.__driver.find_element(By.ID, f"header-search").click()
        time.sleep(1)
        self.__input_field = self.__driver.find_element(By.CLASS_NAME, 'search-input__input-25c7a1')
        self.__input_field.send_keys(name)
        time.sleep(3)
        teams = self.__driver.find_element(By.CLASS_NAME, 'search-autocomplete-916a6c').text
        if len(teams.replace(' ', '')) == 0:
            status = [0]
        else:
            if name in teams.split('\n'):
                status = [2]
            else:
                status = [1, teams.split('\n')[:5]]
        return status

    def second_phase(self, data):
        self.__input_field.clear()
        self.__input_field.send_keys(data)
        time.sleep(1)
        self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/button').click()
        time.sleep(3)
        matches = self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]').text
        if len(matches.replace(' ', '')) == 0:
            return False
        else:
            return self.future_matches(matches, data)

    def future_matches(self, matches, team_name, max_teams=3):
        confirmed_teams = list()
        confirmed_times = list()
        out = list()
        data = matches.split('\n')
        for item in range(2, len(data), 3):
            index = data[item - 2].index('-')
            if team_name == data[item - 2][index + 2:] or team_name == data[item - 2][:index - 1]:
                try:
                    flag = False
                    for i in self.__month.keys():
                        if i in data[item - 1]:
                            right_date_format = data[item - 1].replace(i, self.__month[i])
                            right_date_format = datetime.strptime(right_date_format, '%d %m %Y, %H:%M')
                            flag = True
                            break
                    if flag:
                        confirmed_times.append(right_date_format)
                        confirmed_teams.append(data[item - 2])
                except:
                    pass
        for i in range(len(confirmed_teams)):
            min_time = min(confirmed_times)
            min_time_unix = time.mktime(min_time.timetuple())
            if len(out) >= max_teams:
                break
            elif min_time_unix > time.time():
                out.append([confirmed_teams[confirmed_times.index(min_time)], min_time])
                confirmed_teams.remove(confirmed_teams[confirmed_times.index(min_time)])
                confirmed_times.remove(min_time)
            else:
                confirmed_teams.remove(confirmed_teams[confirmed_times.index(min_time)])
                confirmed_times.remove(min_time)
        return out

    def __del__(self):
        self.__driver.close()
