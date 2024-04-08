#####################################
#            Created by             #
#               zzsxd               #
#               SBR                 #
#####################################
import json
import os
import glob
import undetected_chromedriver as uc
import time
import sys
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from backend import BuildPhoto
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
        icon_start = 0
        try:
            games_data, icons = self.get_content(formatted_date, sport)
            print(len(icons))
            if 'нет соревнований' not in games_data:
                array_games_data = games_data.split('\n')[3:]
                for index, element in enumerate(array_games_data):
                    if len(element) == 5 and element[2] == ':':
                        if sport != 'basketball':
                            BuildPhoto(icons[icon_start], icons[icon_start + 1], sport)
                            with open(f'img/temp/{sport}/result.png', 'rb') as file:
                                data = file.read()
                        hours = int(array_games_data[index][:2])
                        minutes = int(array_games_data[index][3:])
                        datetime_with_time = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=hours,
                                                                                                           minutes=minutes)
                        if sport != 'basketball':
                            self.__db_acts.update_sport(sport, [datetime_with_time, array_games_data[index + 2],
                                                                array_games_data[index + 4], data])
                            files = glob.glob(os.path.join(f'img/temp/{sport}', '*.*'))
                            for file in files:
                                os.remove(file)
                            icon_start += 2
                        else:
                            self.__db_acts.update_basketball(sport, [datetime_with_time, array_games_data[index + 2],
                                                                array_games_data[index + 4]])

        except Exception as e:
            print(e)

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
            except:
                self.main_script(formatted_date, sport, start_date)
            start_date += timedelta(days=1)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = uc.Chrome()

    def get_content(self, date, sport):
        icons = list()
        self.__driver.get(f'https://www.sport-express.ru/live/{sport}/{date}/')
        time.sleep(2)
        parent = self.__driver.find_element(By.XPATH, f"/html/body/div[2]/section/div[2]/div[1]/div/div/div[4]/div")
        child = parent.find_elements(By.TAG_NAME, 'img')
        for i in child:
            icon = i.get_attribute("src")
            if sport in icon:
                icons.append(icon)
        return parent.text, icons


class Leon:
    def __init__(self, selected_team, sport, math, temp_user_data, user_id):
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
        self.parser(selected_team , sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = uc.Chrome()

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['Leon: матч не найден', -1.00])
        self.__driver.quit()
        return False

    def parser(self, selected_team , sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            selector = 0
            section = 1
            ratios = ['Leon: ', -1.00]
            months = math[0][5:7]
            day = math[0][8:10]
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
                    print(sm, 'leon')
                    print(f"s date {f'{data[i - 2]}'} true date {right_date}", 'leon')
                    if (sm >= 0.75 or (math[1].lower() in g.lower() and math[2].lower() in g.lower())) and f'{data[i - 2]}' == right_date:
                        self.second_task(section, selector, one_line)
                        current_url = self.__driver.current_url
                        index = g.index('-')
                        team1 = g[:index-1]
                        ratio = self.third_task(sport).split('\n')
                        sm1 = SequenceMatcher(a=selected_team.lower(),
                                              b=team1.lower()).ratio()
                        if sm1 >= 0.8:
                            cef = ratio[1]
                        else:
                            cef = ratio[5]
                        if math[1].lower() in team1.lower():
                            ratios[1] = float(cef.replace(',', '.'))
                            ratios.append([math[1], ratio[1], current_url])
                            ratios.append(['ничья', ratio[3], current_url])
                            ratios.append([math[2], ratio[5], current_url])
                        else:
                            ratios[1] = float(cef.replace(',', '.'))
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
        time.sleep(5)
        self.__driver.find_element(By.NAME, 'search').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(5)
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
        time.sleep(5)
        if not one_line:
            self.__driver.find_element(By.XPATH,
                                       f'/html/body/div[3]/div/div/div/div[2]/div/div[1]/div/div[2]/div/section[{section}]/ul/li[{index}]/a').click()
        else:
            self.__driver.find_element(By.XPATH,
                                       f'/html/body/div[3]/div/div/div/div[2]/div/div[1]/div/div[2]/div/section/ul/li[{index}]/a').click()


class OlimpBet:
    def __init__(self, selected_team, sport, math, temp_user_data, user_id):
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
        self.parser(selected_team, sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = uc.Chrome()

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['OlimpBet: матч не найден', -1.00])
        self.__driver.quit()
        return False

    def parser(self, selected_team, sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            ratios = ['OlimpBet: ', -1.00]
            year = math[0][:4]
            months = math[0][5:7]
            day = math[0][8:10]
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
                    print(sm, 'OlimpBet')
                    print(f"s date {f'{data[i + 2][:-6]}'} true date {right_date}", 'OlimpBet')
                    if ((sm >= 0.75 or (math[1].lower() in team1.lower() or math[1].lower() in team2.lower()) and
                        (math[2].lower() in team1.lower() or math[2].lower() in team2.lower()))
                            and data[i + 2][:-6] == right_date):
                        current_url = self.__driver.current_url
                        if sport != 'hockey':
                            ratio1 = data[i+3]
                            ratio2 = data[i+4]
                            ratio3 = data[i+5]
                        else:
                            ratio1 = data[i + 4]
                            ratio2 = data[i + 5]
                            ratio3 = data[i + 6]
                        sm1 = SequenceMatcher(a=selected_team.lower(),
                                              b=team1.lower()).ratio()
                        if sm1 >= 0.8:
                            cef = ratio1
                        else:
                            cef = ratio3
                        if math[1].lower() in team1.lower():
                            ratios[1] = float(cef.replace(',', '.'))
                            ratios.append([math[1], ratio1, current_url])
                            ratios.append(['ничья', ratio2, current_url])
                            ratios.append([math[2], ratio3, current_url])
                        else:
                            ratios[1] = float(cef.replace(',', '.'))
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
        time.sleep(5)
        self.__driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[1]/div/div[1]/input').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(5)
        data = self.__driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div[1]/div/div[2]').text
        return data

    def third_task(self):
        time.sleep(5)
        return self.__driver.find_element(By.XPATH,
                                          '/html/body/div[2]/div/div[4]/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div[2]/div/div/div[1]').text

    def second_task(self, atempt, index):
        time.sleep(5)
        self.__driver.find_element(By.XPATH,
                                   f'/html/body/div[{atempt}]/div/div[2]/div/div/div[{index}]/a').click()


class Pari:
    def __init__(self, selected_team, sport, math, temp_user_data, user_id):
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
        self.parser(selected_team, sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = uc.Chrome()

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['Pari: матч не найден', -1.00])
        self.__driver.quit()
        return False

    def parser(self, selected_team , sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            ratios = ['Pari: ', -1.00]
            flag = False
            element_quanity = 0
            months = math[0][5:7]
            day = math[0][8:10]
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
                    print(sm, 'Pari')
                    print(f"s date {f'{data[i + 1][:-8]}'} true date {right_date}", 'Pari')
                    if ((sm >= 0.75 or (math[1].lower() in team1.lower() or math[1].lower() in team2.lower()) and
                        (math[2].lower() in team1.lower() or math[2].lower() in team2.lower()))
                            and data[i + 1][:-8] == right_date):
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
                            print(ratio)
                            sm1 = SequenceMatcher(a=selected_team.lower(),
                                                  b=ratio[0].lower()).ratio()
                            if sport != 'basketball':
                                if sm1 >= 0.8:
                                    cef = ratio[1]
                                else:
                                    cef = ratio[5]
                                if math[1].lower() in ratio[0].lower():
                                    ratios[1] = float(cef.replace(',', '.'))
                                    ratios.append([math[1], ratio[1], current_url])
                                    ratios.append(['ничья', ratio[3], current_url])
                                    ratios.append([math[2], ratio[5], current_url])
                                else:
                                    ratios[1] = float(cef.replace(',', '.'))
                                    ratios.append([math[1], ratio[5], current_url])
                                    ratios.append(['ничья', ratio[3], current_url])
                                    ratios.append([math[2], ratio[1], current_url])
                            else:
                                if sm1 >= 0.8:
                                    cef = ratio[1]
                                else:
                                    cef = ratio[3]
                                if math[1].lower() in ratio[0].lower():
                                    ratios[1] = float(cef.replace(',', '.'))
                                    ratios.append([math[1], ratio[1], current_url])
                                    ratios.append(['ничья', '-', current_url])
                                    ratios.append([math[2], ratio[3], current_url])
                                else:
                                    ratios[1] = float(cef.replace(',', '.'))
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
        time.sleep(5)
        self.__driver.find_element(By.XPATH, '/html/body/div[5]/div/div/input').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(5)
        search_place = self.__driver.find_element(By.XPATH, '//*[@id="search-container"]')
        data = search_place.text
        return data

    def third_task(self, sport):
        time.sleep(5)
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
        time.sleep(1)
        self.__driver.find_element(By.XPATH,
                                   f'/html/body/div[{atempt}]/div/div[2]/div/div/div[{index}]/a').click()


class FonBet:
    def __init__(self, selected_team, sport, math, temp_user_data, user_id):
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
        self.parser(selected_team, sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = uc.Chrome()

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['FonBet: матч не найден', -1.00])
        self.__driver.quit()
        return False

    def parser(self, selected_team, sport, math, user_id):
        try:
            ratios = ['FonBet: ', -1.00]
            data = self.get_data(math).split('\n')
            element_quanity = 0
            months = math[0][5:7]
            day = math[0][8:10]
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
                    index = g.index('—')
                    team1 = g[:index - 1]
                    team2 = g[index + 2:]
                    sm = SequenceMatcher(a=f'{math[1].lower()} - {math[2].lower()}',
                                         b=f'{team1.lower()} - {team2.lower()}').ratio()
                    print(sm, 'fonbet')
                    print(f"s date {f'{data[i + 1][:-8]}'} true date {right_date}", 'fonbet')
                    if ((sm >= 0.75 or (math[1].lower() in team1.lower() or math[1].lower() in team2.lower())
                        and (math[2].lower() in team1.lower() or math[2].lower() in team2.lower()))
                            and data[i + 1][:-8] == right_date):
                        self.second_task(element_quanity)
                        current_url = self.__driver.current_url
                        ratio = self.third_task(sport).split('\n')
                        sm1 = SequenceMatcher(a=selected_team.lower(),
                                              b=ratio[0].lower()).ratio()
                        if sport != 'basketball':
                            if sm1 >= 0.8:
                                cef = ratio[1]
                            else:
                                cef = ratio[5]
                            if math[1].lower() in ratio[0].lower():
                                ratios[1] = float(cef.replace(',', '.'))
                                ratios.append([math[1], ratio[1], current_url])
                                ratios.append(['ничья', ratio[3], current_url])
                                ratios.append([math[2], ratio[5], current_url])
                            else:
                                ratios[1] = float(cef.replace(',', '.'))
                                ratios.append([math[1], ratio[5], current_url])
                                ratios.append(['ничья', ratio[3], current_url])
                                ratios.append([math[2], ratio[1], current_url])
                        else:
                            if sm1 >= 0.8:
                                cef = ratio[1]
                            else:
                                cef = ratio[3]
                            if math[1].lower() in ratio[0].lower():
                                ratios[1] = float(cef.replace(',', '.'))
                                ratios.append([math[1], ratio[1], current_url])
                                ratios.append(['ничья', '-', current_url])
                                ratios.append([math[2], ratio[3], current_url])
                            else:
                                ratios[1] = float(cef.replace(',', '.'))
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
        element = WebDriverWait(self.__driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/application/div[2]/div[1]/div/div/div/div[1]/div/div[2]/div/span')))
        element.click()
        time.sleep(5)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[3]/div/div/div/div/div/span[1]').click()
        time.sleep(5)
        self.__driver.find_element(By.XPATH,
                                   '/html/body/application/div[2]/div[1]/div/div/div/div[1]/div/div[2]/span[3]').click()
        time.sleep(5)
        self.__driver.find_element(By.XPATH, '/html/body/application/div[3]/div[2]/div[2]/input').send_keys(f'{math[1]} - {math[2]}')
        time.sleep(5)
        return self.__driver.find_element(By.XPATH,
                                         '/html/body/application/div[3]/div[2]/div[3]/div[2]/div/div/div[1]').text

    def third_task(self, sport):
        time.sleep(5)
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
        time.sleep(5)
        self.__driver.find_element(By.XPATH, f'/html/body/application/div[3]/div[2]/div[3]/div[2]/div/div/div[1]/div[2]/div[{index}]').click()


class LigaStavok:
    def __init__(self, selected_team, sport, math, temp_user_data, user_id):
        super(LigaStavok, self).__init__()
        self.__month_r = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                          '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября',
                          '12': 'декабря'}
        self.__driver = None
        self.__temp_data = temp_user_data
        self.__input_field = None
        self.init()
        self.parser(selected_team, sport, math, user_id)

    def init(self):
        options = Options()
        options.add_argument('--start-maximized')
        self.__driver = uc.Chrome()

    def error_parse(self, user_id):
        self.__temp_data.temp_data(user_id)[user_id][4].append(['Лига ставок: матч не найден', -1.00])
        self.__driver.quit()
        return False

    def parser(self, selected_team, sport, math, user_id):
        try:
            data = self.get_data(math).split('\n')
            ratios = ['Лига ставок: ', -1.00]
            element_quanity = 0
            months = math[0][5:7]
            day = math[0][8:10]
            if day[0] == '0':
                day = day[1]
            right_date = f'{day} {self.__month_r[months]}'
            for i, g in enumerate(data):
                element_quanity += 1
                if ' - ' in g:
                    index = g.index('-')
                    team1 = g[:index - 1]
                    team2 = g[index + 2:]
                    sm = SequenceMatcher(a=f'{math[1].lower()} - {math[2].lower()}',
                                         b=f'{team1.lower()} - {team2.lower()}').ratio()
                    print(sm, 'liga')
                    print(f"s date {f'{data[i + 1][:-12]}'} true date {right_date}", 'liga')
                    if ((sm >= 0.75 or (math[1].lower() in team1.lower() or math[1].lower() in team2.lower())
                         and (math[2].lower() in team1.lower() or math[2].lower() in team2.lower()))
                            and data[i + 1][:-12] == right_date):
                        self.choose_match(element_quanity)
                        ratio = self.get_ratio().split('\n')[0:7]
                        current_url = self.__driver.current_url
                        sm1 = SequenceMatcher(a=selected_team.lower(),
                                              b=ratio[0].lower()).ratio()
                        if sm1 >= 0.8:
                            cef = ratio[1]
                        else:
                            cef = ratio[5]
                        if math[1].lower() in ratio[0].lower():
                            ratios[1] = float(cef.replace(',', '.'))
                            ratios.append([math[1], ratio[1], current_url])
                            ratios.append(['ничья', ratio[3], current_url])
                            ratios.append([math[2], ratio[5], current_url])
                        else:
                            ratios[1] = float(cef.replace(',', '.'))
                            ratios.append([math[1], ratio[5], current_url])
                            ratios.append(['ничья', ratio[3], current_url])
                            ratios.append([math[2], ratio[1], current_url])
                        self.__temp_data.temp_data(user_id)[user_id][4].append(ratios)
                        self.__driver.quit()
                        return ratios

            self.error_parse(user_id)
        except Exception as e:
            print(e, 'liga')
            self.error_parse(user_id)

    def get_data(self, metch):
        self.__driver.get('https://www.ligastavok.ru/')
        time.sleep(5)
        element = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="header-search"]')))
        element.click()
        time.sleep(5)
        self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/input').send_keys(f'{metch[1]} - {metch[2]}')
        time.sleep(5)
        self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/button').click()
        time.sleep(5)
        return self.__driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]').text

    def choose_match(self, index):
        time.sleep(5)
        element = self.__driver.find_element(By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div/a[{index}]')
        self.__driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ActionChains(self.__driver).move_to_element(element).click().perform()

    def get_ratio(self):
        time.sleep(5)
        data = self.__driver.find_elements(By.CLASS_NAME, f'market__outcomes-96e4e5')
        while True:
            for i in data:
                cart = i.text
                if len(cart.split('\n')) >= 7:
                    return cart

