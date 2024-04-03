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
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
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


class UpdateMatches:
    def __init__(self, db_action, sport):
        super(UpdateMatches, self).__init__()
        self.__db_acts = db_action
        self.__driver = None
        self.__input_field = None
        self.init()
        self.updater(sport)

    def main_script(self, formatted_date, sport, start_date):
        games_data = self.get_content(formatted_date, sport)
        if 'нет соревнований' not in games_data:
            cleaned_games = list()
            array_games_data = games_data.split('\n')[3:]
            for index, element in enumerate(array_games_data):
                try:
                    if len(element) == 5 and element[2] == ':':
                        hours = int(array_games_data[index][:2])
                        minutes = int(array_games_data[index][3:])
                        datetime_with_time = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=hours, minutes=minutes)
                        self.__db_acts.update_sport(sport, [datetime_with_time, array_games_data[index + 2], array_games_data[index + 4]])
                except Exception as e:
                    print(e)
            print(cleaned_games)

    def updater(self, sport):
        start_date = datetime.now().date()
        real_start = start_date
        while True:
            formatted_date = start_date.strftime("%d-%m-%Y")
            try:
                if real_start + timedelta(days=365) <= start_date:
                    self.__driver.close()
                    break
                elif start_date <= datetime.strptime(self.__db_acts.last_sport_date(sport), "%Y-%m-%d %H:%M:%S").date():
                    pass
                else:
                    self.main_script(formatted_date, sport, start_date)
            except Exception as e:
                print(e)
                self.main_script(formatted_date, sport, start_date)
            start_date += timedelta(days=1)

    def init(self):
        service = Service(executable_path='chromedriver.exe')
        self.__driver = uc.Chrome(service=service)

    def get_content(self, date, sport):
        self.__driver.get(f'https://www.sport-express.ru/live/{sport}/{date}/')
        time.sleep(1)
        return self.__driver.find_element(By.XPATH, f"/html/body/div[2]/section/div[2]/div[1]/div/div/div[4]/div").text


class FonBet:
    def __init__(self):
        super(FonBet, self).__init__()
        self.__driver = None
        self.__input_field = None

    def init(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless=new")  # for Chrome >= 109
        self.__driver = uc.Chrome()

    def parser(self, name):
        self.init()
        self.__driver.get('https://www.fon.bet/')
        time.sleep(10)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[2]/div[1]/div/div/div/div[1]/div/div[2]/div/span').click()
        time.sleep(0.5)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[3]/div/div/div/div/div/span[1]').click()
        time.sleep(1)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[2]/div[1]/div/div/div/div[1]/div/div[2]/span[3]').click()
        time.sleep(1)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[3]/div[2]/div[2]/input').send_keys(name[0])
        time.sleep(3)
        print(self.__driver.find_element(By.XPATH, '/html/body/application/div[3]/div[2]/div[3]/div[2]/div[1]/div/div[1]').text)


class LigaStavok:
    def __init__(self, math, temp_user_data, user_id):
        super(LigaStavok, self).__init__()
        self.__month = {'01':'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                        '12': 'декабря'}
        self.__driver = None
        self.__temp_data = temp_user_data
        self.__input_field = None
        self.init()
        self.parser(math, user_id)

    def init(self):
        service = Service(executable_path='chromedriver.exe')
        self.__driver = uc.Chrome(service=service)

    def parser(self, math, user_id):
        data = self.get_data(math).split('\n')
        dates = list()
        ratios = ['Лига ставок * ']
        for i in range(2, len(data), 3):
            dates.append(data[i - 1])
        year = math[0][:4]
        months = math[0][5:7]
        day = math[0][8:10]
        times = math[0][11:16]
        if day[0] == '0':
            day = day[1]
        right_date = f'{day} {self.__month[months]} {year}, {times}'
        print(dates)
        print(right_date)
        if right_date in dates:
            self.choose_match(dates.index(right_date)+1)
            ratio = self.get_ratio().split('\n')[1:7]
            print(ratio)
            if math[1] in ratio[0]:
                ratios.append([math[1], ratio[1]])
                ratios.append([math[2], ratio[5]])
            else:
                ratios.append([math[1], ratio[5]])
                ratios.append([math[2], ratio[1]])
            self.__temp_data.temp_data(user_id)[user_id][4].append(ratios)
            self.__driver.close()
            return ratios

        else:
            self.__temp_data.temp_data(user_id)[user_id][4].append(['Лига ставок * ERROR'])
            self.__driver.close()
            return False

    def get_data(self, metch):
        self.__driver.get('https://www.ligastavok.ru/')
        time.sleep(5)
        self.__driver.find_element(By.XPATH, '//*[@id="header-search"]').click()
        time.sleep(0.5)
        self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/input').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(2)
        self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/button').click()
        time.sleep(2)
        return self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]').text

    def choose_match(self, index):
        time.sleep(1)
        element = self.__driver.find_element(By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div/a[{index}]')
        self.__driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ActionChains(self.__driver).move_to_element(element).click().perform()

    def get_ratio(self):
        time.sleep(10)
        return self.__driver.find_element(By.CLASS_NAME, 'part__markets-86eb26').text
