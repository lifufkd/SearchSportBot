#####################################
#            Created by             #
#               SBR                 #
#####################################
config_name = 'secrets.json'
#####################################
import os
import telebot
import schedule
import time
import copy
import platform
import pyvirtualdisplay
import threading
from threading import Lock
from os import listdir
from os.path import isfile, join
from datetime import datetime
from parser import ConfigParser, UpdateMatches, FonBet, LigaStavok, Pari, BetCity, Leon, OlimpBet
from frontend import Bot_inline_btns
from backend import TempUserData, DbAct, Excel
from db import DB
#####################################


def sync_db():
    if datetime.now().month == 1 and datetime.now().day == 1 or config.get_config()['update_every_day']:
        for sport in ['football', 'hockey', 'basketball']:
            threading.Thread(target=UpdateMatches, args=(db_actions, sport)).start()


def choose_sport(user_id, sport):
    temp_user_data.temp_data(user_id)[user_id][0] = 0
    temp_user_data.temp_data(user_id)[user_id][1] = sport
    bot.send_message(user_id, 'Напишите название команды')


def matches(data):
    s = ''
    for i, g in enumerate(data):
        year = g[0][2:4]
        months = g[0][5:7]
        day = g[0][8:10]
        times = g[0][11:16]
        s += f'{i+1}. {g[1]} - {g[2]} {f"{day}.{months}.{year} {times}"}\n'
    return s


def schedule_worker():
    while True:
        schedule.run_pending()
        time.sleep(1)


def cleaner():
    if platform.system() == 'Windows':
        path = f"{os.getenv('APPDATA')}\\undetected_chromedriver"
    else:
        path = f"{os.getenv('HOME')}/.local/share/undetected_chromedriver"
    for f in listdir(path):
        if isfile(f'{path}/{f}'):
            try:
                os.remove(f'{path}/{f}')
            except:
                pass


def waiter(user_id, s='', c=0):
    ratios = list()
    out = list()
    temp = list()
    buttons = Bot_inline_btns()
    while True:
        c+=1
        if len(temp_user_data.temp_data(user_id)[user_id][4]) == 6:
            break
        elif c >= 180:
            break
        time.sleep(1)
    for i in temp_user_data.temp_data(user_id)[user_id][4]:
        ratios.append(i[1])
    ratios.sort()
    for i in reversed(ratios):
        for g in temp_user_data.temp_data(user_id)[user_id][4]:
            if g[1] == i and g[0] not in temp:
                if 'матч не найден' not in g[0]:
                    out.append(f'<a href="{g[2][2]}">• {g[0]}{g[2][0]} <b>{g[2][1]}</b> | {g[3][0]} <b>{g[3][1]}</b> | {g[4][0]} <b>{g[4][1]}</b></a>\n\n')
                else:
                    out.append(f'{g[0]}\n')
                temp.append(g[0])
    for i in out:
        s += i
    temp_user_data.temp_data(user_id)[user_id][4] = copy.deepcopy([])
    temp_user_data.temp_data(user_id)[user_id][0] = None
    cleaner()
    bot.send_message(user_id, s, parse_mode='html', disable_web_page_preview=True)
    time.sleep(1)
    if s.count('матч не найден') == 6:
        bot.send_message(user_id, 'Матч вижу, но не вижу коэффициенты в БК. Возможно, букмекеры еще не дали коэффициенты.\nХотите найти ещё кэфы?', reply_markup=buttons.new_btns())
    else:
        bot.send_message(user_id,
                         'Хотите найти ещё кэфы?',
                         reply_markup=buttons.new_btns())
    ### функция пользовательского поиска
    #if 'матч не найден' in s:
        #temp_user_data.temp_data(user_id)[user_id][0] = 3
        #bot.send_message(user_id, 'Не все кэфы нашлись? Напишите название матча в формате <b>"Локомотив - ЦСКА"</b>, '
                                  #'результат будет лучше!', parse_mode='html')



def get_all_ratio(user_id):
    selected_teams = temp_user_data.temp_data(user_id)[user_id][3]
    inp_team = temp_user_data.temp_data(user_id)[user_id][5]
    sport = temp_user_data.temp_data(user_id)[user_id][1]
    temp_user_data.temp_data(user_id)[user_id][0] = 2
    bot.send_message(user_id, f'Ищу лучшие кэфы на матч "{temp_user_data.temp_data(user_id)[user_id][3][1]} - {temp_user_data.temp_data(user_id)[user_id][3][2]}" 🔎\nМожет занять до 2 минут ⏳')
    threading.Thread(target=LigaStavok, args=(inp_team, sport, selected_teams, temp_user_data, user_id)).start()# work all
    threading.Thread(target=FonBet, args=(inp_team, sport, selected_teams, temp_user_data, user_id)).start()  # work all
    threading.Thread(target=OlimpBet, args=(inp_team, sport, selected_teams, temp_user_data, user_id)).start()# work all
    threading.Thread(target=Pari, args=(inp_team, sport, selected_teams, temp_user_data, user_id)).start() # work all
    threading.Thread(target=BetCity, args=(inp_team, sport, selected_teams, temp_user_data, user_id)).start()  # work all
    threading.Thread(target=Leon, args=(inp_team, sport, selected_teams, temp_user_data, user_id)).start()# work fine
    threading.Thread(target=waiter, args=(user_id, )).start()


def main():
    @bot.message_handler(commands=['start', 'admin'])
    def start_msg(message):
        user_id = message.from_user.id
        buttons = Bot_inline_btns()
        command = message.text.replace('/', '')
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        if command == 'start':
            bot.send_message(message.chat.id, 'Я - ваш помощник в мире ставок на спорт 🏆\nПомогу найти самые выгодные '
                                              'коэффициенты среди лучших\nбукмекерских компаний 🎯\n\nКак это работает:\nВыберите'
                                              ' вид спорта ->\nНапишите название команды ->\nВыберите интересующий вас матч\n\n'
                                              ' Найду коэффициенты на это событие по разным БК, чтобы вы могли сделать '
                                              'самую выгодную ставку 💰\n\nВот по каким букмекерам я могу искать:\n\n'
                                              '<a href="https://www.fon.bet/">FonBet</a>\n'
                                              '<a href="https://www.ligastavok.ru/">Лига ставок</a>\n'
                                              '<a href="https://www.pari.ru/">Pari</a>\n'
                                              '<a href="https://leon.ru/">Леон</a>\n'
                                              '<a href="https://betcity.ru/ru">БэтСити</a>\n'
                                              '<a href="https://www.olimp.bet/">Olimpbet</a>\n',
                             reply_markup=buttons.start_btns(), parse_mode='html', disable_web_page_preview=True)
        elif command == 'admin':
            if db_actions.user_is_admin(user_id):
                bot.send_message(user_id, 'Вы попали в админ панель', reply_markup=buttons.admin_btns())

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        buttons = Bot_inline_btns()
        user_id = call.message.chat.id
        if db_actions.user_is_existed(user_id):
            code = temp_user_data.temp_data(user_id)[user_id][0]
            if command[:5] == 'sport':
                choose_sport(user_id, command[5:])
            elif command[:4] == 'game' and code == 1:
                if command[4:] == 'Выбрать спорт':
                    temp_user_data.temp_data(user_id)[user_id][0] = None
                    bot.send_message(user_id, 'Выберите спорт', reply_markup=buttons.new_btns())
                else:
                    temp_user_data.temp_data(user_id)[user_id][3] = temp_user_data.temp_data(user_id)[user_id][2][int(command[4:])]
                    get_all_ratio(user_id)
            elif command == 'update_often_teams':
                temp_user_data.temp_data(user_id)[user_id][0] = 4
                bot.send_message(user_id, 'Отправьте новую таблицу в формате .xlsx')

    @bot.message_handler(content_types=['text', 'photo', 'document'])
    def text_message(message):
        user_input = message.text
        user_id = message.chat.id
        buttons = Bot_inline_btns()
        code = temp_user_data.temp_data(user_id)[user_id][0]
        if db_actions.user_is_existed(user_id):
            match user_input:
                case 'Футбол ⚽️':
                    choose_sport(user_id, 'football')
                case 'Хоккей🏒':
                    choose_sport(user_id, 'hockey')
                case 'Баскетбол 🏀':
                    choose_sport(user_id, 'basketball')
            match code:
                case 0:
                    if user_input is not None:
                        full_data = db_actions.get_team_matches(temp_user_data.temp_data(user_id)[user_id][1], user_input)
                        temp_user_data.temp_data(user_id)[user_id][5] = user_input
                        if len(full_data) > 0:
                            if len(full_data) == 1:
                                temp_user_data.temp_data(user_id)[user_id][3] = full_data[0]
                                get_all_ratio(user_id)
                            else:
                                temp_user_data.temp_data(user_id)[user_id][2] = full_data
                                temp_user_data.temp_data(user_id)[user_id][0] = 1
                                s = matches(full_data)
                                bot.send_message(user_id, f'Для этой команды нашлось {len(full_data)} матчей: \n{s}',
                                                 reply_markup=buttons.games_btns(len(full_data)))
                        else:
                            bot.send_message(user_id, 'Попробуйте написать по другому: не нашел команду :(', reply_markup=buttons.new_btns())
                    else:
                        bot.send_message(user_id, 'Это не текст!')
                case 3:
                    if user_input is not None:
                        if '-' in user_input:
                            index = user_input.index('-')
                            team1 = user_input[:index]
                            team2 = user_input[index+1:]
                            date = temp_user_data.temp_data(user_id)[user_id][3][0]
                            temp_user_data.temp_data(user_id)[user_id][3] = [date, team1, team2]
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            get_all_ratio(user_id)
                        else:
                            bot.send_message(user_id, 'Без знака "-" я не понимаю как отличить 2 команды. Напишите ещё раз')
                    else:
                        bot.send_message(user_id, 'Это не текст!')
            if db_actions.user_is_admin(user_id):
                match code:
                    case 4:
                        document_id = message.document.file_id
                        file_info = bot.get_file(document_id)
                        downloaded_file = bot.download_file(file_info.file_path)
                        with open(config.get_config()['teams_xlsx_doc'], 'wb') as new_file:
                            new_file.write(downloaded_file)
                        data = excel.read_teams_names()
                        db_actions.update_overwrite_teams(data)

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    excel = Excel(config, db, db_actions)
    threading.Thread(target=schedule_worker).start()
    schedule.every().day.at('00:00').do(sync_db)
    sync_db()
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
