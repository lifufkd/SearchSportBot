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
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.__db_acts.clean_db()
        while True:
            formatted_date = start_date.strftime("%d-%m-%Y")
            try:
                if real_start + timedelta(days=365) <= start_date:
                    self.__driver.quit()
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
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = webdriver.Chrome(options=options)

    def get_content(self, date, sport):
        self.__driver.get(f'https://www.sport-express.ru/live/{sport}/{date}/')
        time.sleep(1)
        return self.__driver.find_element(By.XPATH, f"/html/body/div[2]/section/div[2]/div[1]/div/div/div[4]/div").text


class Leon:
    def __init__(self, sport, math, temp_user_data, user_id):
        super(Leon, self).__init__()
        self.__month = {'01':'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                        '12': 'декабря'}
        self.__month_r = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                          '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                          '12': 'декабря'}
        self.__driver = None
        self.__temp_data = temp_user_data
        self.__input_field = None
        self.init()
        self.parser(sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = webdriver.Chrome(options=options)

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['Leon: матч не найден'])
        self.__driver.quit()
        return False

    def parser(self, sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            print(data)
            selector = 0
            section = 1
            ratios = ['Leon: ']
            months = math[0][5:7]
            day = math[0][8:10]
            times = math[0][11:16]
            right_date = f'{day}.{months}'
            if 'Линия' in data[0]:
                one_line = True
            else:
                one_line = False
            for i, g in enumerate(data):
                if 'Линия' in g:
                    selector = 0
                    section += 1
                elif ' - ' in g:
                    selector += 1
                    sm = SequenceMatcher(a=f'{math[1].lower()} - {math[2].lower()}', b=g.lower()).ratio()
                    if sm >= 0.75 and f'{data[i - 2]}' == right_date:
                        self.second_task(section, selector, one_line)
                        current_url = self.__driver.current_url
                        index = g.index('-')
                        team1 = g[:index-1]
                        ratio = self.third_task(sport).split('\n')
                        print(ratio)
                        if math[1].lower() in team1.lower():
                            ratios.append([math[1], ratio[1], current_url])
                            ratios.append(['ничья', ratio[3], current_url])
                            ratios.append([math[2], ratio[5], current_url])
                        else:
                            ratios.append([math[1], ratio[5], current_url])
                            ratios.append(['ничья', ratio[3], current_url])
                            ratios.append([math[2], ratio[1], current_url])

                        self.__temp_data.temp_data(user_id)[user_id][4].append(ratios)
                        self.__driver.quit()
                        return ratios
            self.error_parse(user_id)
        except Exception as e:
            print(e)
            self.error_parse(user_id)

    def get_data(self, metch):
        self.__driver.get('https://leon.ru/')
        time.sleep(2)
        self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.__driver.execute_script("window.scrollTo(0, 0);")
        element = WebDriverWait(self.__driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/header/div/div/div/div[2]/div[1]/button')))
        element.click()
        time.sleep(3)
        self.__driver.find_element(By.NAME, 'search').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(3)
        data = self.__driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div/div[1]/div').text
        return data

    def third_task(self, sport):
        time.sleep(5)
        match sport:
            case 'football':
                return self.__driver.find_element(By.XPATH,
                                                  '/html/body/div[2]/section/div/main/div[2]/div[3]/div/div/div[1]/div[3]/div/div/div/div/div/div[2]/div[3]').text
            case 'basketball':
                return self.__driver.find_element(By.XPATH,
                                                  '/html/body/div[2]/section/div/main/div[2]/div[3]/div/div/div[1]/div[4]/div[2]/div[1]/section[1]/article/div[2]/div').text
            case 'hockey':
                return self.__driver.find_element(By.XPATH,
                                          '/html/body/div[2]/section/div/main/div[2]/div[3]/div/div/div[1]/div[3]/div/div/div/div/div/div[2]/div[3]').text

    def second_task(self, section, index, one_line):
        time.sleep(3)
        if not one_line:
            self.__driver.find_element(By.XPATH,
                                       f'/html/body/div[3]/div/div/div/div[2]/div/div[1]/div/div[2]/div/section[{section}]/ul/li[{index}]/a').click()
        else:
            self.__driver.find_element(By.XPATH,
                                       f'/html/body/div[3]/div/div/div/div[2]/div/div[1]/div/div[2]/div/section/ul/li[{index}]/a').click()


class OlimpBet:
    def __init__(self, sport, math, temp_user_data, user_id):
        super(OlimpBet, self).__init__()
        self.__month = {'01':'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                        '12': 'декабря'}
        self.__month_r = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                          '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                          '12': 'декабря'}
        self.__driver = None
        self.__temp_data = temp_user_data
        self.__input_field = None
        self.init()
        self.parser(sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = webdriver.Chrome(options=options)

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['OlimpBet: матч не найден'])
        self.__driver.quit()
        return False

    def parser(self, sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            ratios = ['OlimpBet: ']
            year = math[0][:4]
            months = math[0][5:7]
            day = math[0][8:10]
            times = math[0][11:16]
            if day[0] == '0':
                day = day[1]
            if datetime.strptime(math[0], '%Y-%m-%d %H:%M:%S').date() == datetime.now().date():
                day = 'Сегодня'
                right_date = f'{day}'
            elif datetime.strptime(math[0], '%Y-%m-%d %H:%M:%S').date() == (datetime.now()+timedelta(days=1)).date():
                day = 'Завтра'
                right_date = f'{day}'
            else:
                right_date = f'{day}.{months}.{year}'
            for i, g in enumerate(data):
                if ' - ' in g:
                    team1 = data[i-1]
                    team2 = data[i+1]
                    sm = SequenceMatcher(a=f'{math[1].lower()} - {math[2].lower()}',
                                         b=f'{team1.lower()} - {team2.lower()}').ratio()
                    if sm >= 0.75 and data[i + 2][:-6] == right_date:
                        current_url = self.__driver.current_url
                        if sport != 'hockey':
                            ratio1 = data[i+3]
                            ratio2 = data[i+4]
                            ratio3 = data[i+5]
                        else:
                            ratio1 = data[i + 4]
                            ratio2 = data[i + 5]
                            ratio3 = data[i + 6]
                        if math[1].lower() in team1.lower():
                            ratios.append([math[1], ratio1, current_url])
                            ratios.append(['ничья', ratio2, current_url])
                            ratios.append([math[2], ratio3, current_url])
                        else:
                            ratios.append([math[1], ratio3, current_url])
                            ratios.append(['ничья', ratio2, current_url])
                            ratios.append([math[2], ratio1, current_url])
                        self.__temp_data.temp_data(user_id)[user_id][4].append(ratios)
                        self.__driver.quit()
                        return ratios
            self.error_parse(user_id)
        except Exception as e:
            print(e)
            self.error_parse(user_id)

    def get_data(self, metch):
        self.__driver.get('https://www.olimp.bet/')
        time.sleep(5)
        self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.__driver.execute_script("window.scrollTo(0, 0);")
        element = WebDriverWait(self.__driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/div/div[2]/div/div[1]/div/div[2]/div[1]/div[1]/div/button[2]')))
        element.click()
        time.sleep(3)
        search_place = self.__driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[1]/div/div[1]/input').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(3)
        data = self.__driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div[1]/div/div[2]').text
        return data

    def third_task(self):
        time.sleep(3)
        return self.__driver.find_element(By.XPATH,
                                          '/html/body/div[2]/div/div[4]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div[2]/div/div/div[1]').text

    def second_task(self, atempt, index):
        time.sleep(3)
        self.__driver.find_element(By.XPATH,
                                   f'/html/body/div[{atempt}]/div/div[2]/div/div/div[{index}]/a').click()


class Pari:
    def __init__(self, sport, math, temp_user_data, user_id):
        super(Pari, self).__init__()
        self.__month = {'01':'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                        '12': 'декабря'}
        self.__month_r = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                          '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                          '12': 'декабря'}
        self.__driver = None
        self.__temp_data = temp_user_data
        self.__input_field = None
        self.init()
        self.parser(sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = webdriver.Chrome(options=options)

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['Pari: матч не найден'])
        self.__driver.quit()
        return False

    def parser(self, sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            ratios = ['Pari: ']
            flag = False
            element_quanity = 0
            months = math[0][5:7]
            day = math[0][8:10]
            times = math[0][11:16]
            if day[0] == '0':
                day = day[1]
            if datetime.strptime(math[0], '%Y-%m-%d %H:%M:%S').date() == datetime.now().date():
                day = 'Сегодня'
                right_date = f'{day}'
            elif datetime.strptime(math[0], '%Y-%m-%d %H:%M:%S').date() == (datetime.now()+timedelta(days=1)).date():
                day = 'Завтра'
                right_date = f'{day}'
            else:
                right_date = f'{day} {self.__month_r[months]}'
            for i, g in enumerate(data):
                if '—' in g:
                    index = g.index('—')
                    team1 = g[:index - 1]
                    team2 = g[index + 2:]
                    sm = SequenceMatcher(a=f'{math[1].lower()} - {math[2].lower()}',
                                         b=f'{team1.lower()} - {team2.lower()}').ratio()
                    if sm >= 0.75 and data[i + 1][:-8] == right_date:
                        for k in range(10):
                            try:
                                self.second_task(k, element_quanity)
                                flag = True
                                break
                            except:
                                pass
                        if flag:
                            current_url = self.__driver.current_url
                            ratio = self.third_task(sport).split('\n')
                            if sport != 'basketball':
                                if math[1].lower() in ratio[0].lower():
                                    ratios.append([math[1], ratio[1], current_url])
                                    ratios.append(['ничья', ratio[3], current_url])
                                    ratios.append([math[2], ratio[5], current_url])
                                else:
                                    ratios.append([math[1], ratio[5], current_url])
                                    ratios.append(['ничья', ratio[3], current_url])
                                    ratios.append([math[2], ratio[1], current_url])
                            else:
                                if math[1].lower() in ratio[0].lower():
                                    ratios.append([math[1], ratio[1], current_url])
                                    ratios.append(['ничья', '-', current_url])
                                    ratios.append([math[2], ratio[3], current_url])
                                else:
                                    ratios.append([math[1], ratio[3], current_url])
                                    ratios.append(['ничья', '-', current_url])
                                    ratios.append([math[2], ratio[1], current_url])
                            self.__temp_data.temp_data(user_id)[user_id][4].append(ratios)
                            self.__driver.quit()
                            return ratios
                        else:
                            self.error_parse(user_id)
                element_quanity += 1
            self.error_parse(user_id)
        except Exception as e:
            print(e)
            self.error_parse(user_id)


    def get_data(self, metch):
        self.__driver.get('https://www.pari.ru/')
        time.sleep(5)
        self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.__driver.execute_script("window.scrollTo(0, 0);")
        element = WebDriverWait(self.__driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[2]/header/div[2]/div/div[2]/a')))
        element.click()
        time.sleep(3)
        self.__driver.find_element(By.XPATH, '/html/body/div[5]/div/div/input').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(3)
        search_place = self.__driver.find_element(By.XPATH, '//*[@id="search-container"]')
        data = search_place.text
        return data

    def third_task(self, sport):
        time.sleep(3)
        match sport:
            case 'football':
                return self.__driver.find_element(By.XPATH,
                                                  '/html/body/div[2]/div/div[4]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div[2]/div/div/div[1]').text
            case 'hockey':
                return self.__driver.find_element(By.XPATH,
                                                  '/html/body/div[2]/div/div[4]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div[3]/div[1]/div/div[1]/div[2]/div[2]/div[1]/div[2]/div/div/div[1]').text
            case 'basketball':
                return self.__driver.find_element(By.XPATH,
                                                  '/html/body/div[2]/div/div[4]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div').text

    def second_task(self, atempt, index):
        time.sleep(3)
        self.__driver.find_element(By.XPATH,
                                   f'/html/body/div[{atempt}]/div/div[2]/div/div/div[{index}]/a').click()


class FonBet:
    def __init__(self, sport, math, temp_user_data, user_id):
        super(FonBet, self).__init__()
        self.__month = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
                        'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11',
                        'декабря': '12'}
        self.__month_r = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                        '12': 'декабря'}
        self.__driver = None
        self.__temp_data = temp_user_data
        self.__input_field = None
        self.init()
        self.parser(sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = webdriver.Chrome(options=options)

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['FonBet: матч не найден'])
        self.__driver.quit()
        return False

    def parser(self, sport, math, user_id):
        try:
            ratios = ['FonBet: ']
            data = self.get_data(math).split('\n')
            element_quanity = 0
            months = math[0][5:7]
            day = math[0][8:10]
            times = math[0][11:16]
            if day[0] == '0':
                day = day[1]
            if datetime.strptime(math[0], '%Y-%m-%d %H:%M:%S').date() == datetime.now().date():
                day = 'Сегодня'
                right_date = f'{day}'
            elif datetime.strptime(math[0], '%Y-%m-%d %H:%M:%S').date() == (datetime.now() + timedelta(days=1)).date():
                day = 'Завтра'
                right_date = f'{day}'
            else:
                right_date = f'{day} {self.__month_r[months]}'
            for i, g in enumerate(data):
                if '—' in g:
                    my_math = f'{math[1]} - {math[2]}'
                    index = g.index('—')
                    team1 = g[:index - 1]
                    team2 = g[index + 2:]
                    sm = SequenceMatcher(a=f'{math[1].lower()} - {math[2].lower()}',
                                         b=f'{team1.lower()} - {team2.lower()}').ratio()
                    if sm >= 0.75 and data[i + 1][:-8] == right_date:
                        self.second_task(element_quanity)
                        current_url = self.__driver.current_url
                        ratio = self.third_task(sport).split('\n')
                        if sport != 'basketball':
                            if math[1].lower() in ratio[0].lower():
                                ratios.append([math[1], ratio[1], current_url])
                                ratios.append(['ничья', ratio[3], current_url])
                                ratios.append([math[2], ratio[5], current_url])
                            else:
                                ratios.append([math[1], ratio[5], current_url])
                                ratios.append(['ничья', ratio[3], current_url])
                                ratios.append([math[2], ratio[1], current_url])
                        else:
                            if math[1].lower() in ratio[0].lower():
                                ratios.append([math[1], ratio[1], current_url])
                                ratios.append(['ничья', '-', current_url])
                                ratios.append([math[2], ratio[3], current_url])
                            else:
                                ratios.append([math[1], ratio[3], current_url])
                                ratios.append(['ничья', '-', current_url])
                                ratios.append([math[2], ratio[1], current_url])
                        self.__temp_data.temp_data(user_id)[user_id][4].append(ratios)
                        self.__driver.quit()
                        return ratios
                element_quanity += 1
            self.error_parse(user_id)
        except Exception as e:
            print(e)
            self.error_parse(user_id)


    def get_data(self, math):
        self.__driver.get('https://www.fon.bet/')
        time.sleep(5)
        self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.__driver.execute_script("window.scrollTo(0, 0);")
        element = WebDriverWait(self.__driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/application/div[2]/div[1]/div/div/div/div[1]/div/div[2]/div/span')))
        element.click()
        time.sleep(3)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[3]/div/div/div/div/div/span[1]').click()
        time.sleep(3)
        self.__driver.find_element(By.XPATH,
                                   '/html/body/application/div[2]/div[1]/div/div/div/div[1]/div/div[2]/span[3]').click()
        time.sleep(3)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[3]/div[2]/div[2]/input').send_keys(f'{math[1]} - {math[2]}')
        time.sleep(3)
        return self.__driver.find_element(By.XPATH,
                                         '/html/body/application/div[3]/div[2]/div[3]/div[2]/div/div/div[1]').text

    def third_task(self, sport):
        time.sleep(3)
        match sport:
            case 'football':
                return self.__driver.find_element(By.XPATH, '/html/body/application/div[2]/div[1]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div/div/div[1]').text
            case 'hockey':
                return self.__driver.find_element(By.XPATH,
                                                            '/html/body/application/div[2]/div[1]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div[1]/div/div[1]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/div[1]').text
            case 'basketball':
                return self.__driver.find_element(By.XPATH,
                                                            '/html/body/application/div[2]/div[1]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/div').text

    def second_task(self, index):
        time.sleep(3)
        self.__driver.find_element(By.XPATH, f'/html/body/application/div[3]/div[2]/div[3]/div[2]/div/div/div[1]/div[2]/div[{index}]').click()


class LigaStavok:
    def __init__(self, sport, math, temp_user_data, user_id):
        super(LigaStavok, self).__init__()
        self.__month = {'01':'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                        '12': 'декабря'}
        self.__driver = None
        self.__temp_data = temp_user_data
        self.__input_field = None
        self.init()
        self.parser(sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = webdriver.Chrome(options=options)

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['Лига ставок: матч не найден'])
        self.__driver.quit()
        return False

    def parser(self, sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            dates = list()
            ratios = ['Лига ставок: ']
            for i in range(2, len(data), 3):
                dates.append(data[i - 1])
            year = math[0][:4]
            months = math[0][5:7]
            day = math[0][8:10]
            times = math[0][11:16]
            if day[0] == '0':
                day = day[1]
            right_date = f'{day} {self.__month[months]} {year}, {times}'
            if right_date in dates:
                self.choose_match(dates.index(right_date) + 1)
                ratio = self.get_ratio().split('\n')[0:7]
                print(ratio)
                current_url = self.__driver.current_url
                if math[1].lower() in ratio[0].lower():
                    ratios.append([math[1], ratio[1], current_url])
                    ratios.append(['ничья', ratio[3], current_url])
                    ratios.append([math[2], ratio[5], current_url])
                else:
                    ratios.append([math[1], ratio[5], current_url])
                    ratios.append(['ничья', ratio[3], current_url])
                    ratios.append([math[2], ratio[1], current_url])
                self.__temp_data.temp_data(user_id)[user_id][4].append(ratios)
                self.__driver.quit()
                return ratios

            else:
                self.error_parse(user_id)
        except Exception as e:
            print(e)
            self.error_parse(user_id)


    def get_data(self, metch):
        self.__driver.get('https://www.ligastavok.ru/')
        time.sleep(5)
        self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.__driver.execute_script("window.scrollTo(0, 0);")
        element = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="header-search"]')))
        element.click()
        time.sleep(3)
        self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/input').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(3)
        self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/button').click()
        time.sleep(3)
        return self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]').text

    def choose_match(self, index):
        time.sleep(3)
        element = self.__driver.find_element(By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div/a[{index}]')
        self.__driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ActionChains(self.__driver).move_to_element(element).click().perform()

    def get_ratio(self):
        time.sleep(3)
        return self.__driver.find_element(By.CLASS_NAME, 'market__outcomes-96e4e5').text

