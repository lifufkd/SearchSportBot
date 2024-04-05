#####################################
#            Created by             #
#               SBR                 #
#####################################
import copy

config_name = 'secrets.json'
#####################################
import os
import telebot
import schedule
import time
import platform
import threading
from threading import Lock
from os import listdir
from os.path import isfile, join
from datetime import datetime
from parser import ConfigParser, UpdateMatches, FonBet, LigaStavok, Pari, OlimpBet, Leon
from frontend import Bot_inline_btns
from backend import TempUserData, DbAct
from db import DB
#####################################


def sync_db():
    if datetime.now().month == 1 and datetime.now().day == 1:
        for sport in ['football', 'hockey', 'basketball']:
            threading.Thread(target=UpdateMatches, args=(db_actions, sport)).start()


def schedule_worker():
    while True:
        schedule.run_pending()
        time.sleep(1)


def cleaner():
    if platform.system() == 'Windows':
        path = f"{os.getenv('APPDATA')}\\undetected_chromedriver"
    else:
        path = f"{os.getenv('APPDATA')}\\"
    for f in listdir(path):
        if isfile(f'{path}\\{f}'):
            try:
                os.remove(f'{path}\\{f}')
            except:
                pass


def waiter(user_id, status, s=''):
    while True:
        if len(temp_user_data.temp_data(user_id)[user_id][4]) == 5:
            break
        time.sleep(1)
    for i in temp_user_data.temp_data(user_id)[user_id][4]:
        if 'матч не найден' not in i[0]:
            s += f'{i[0]}{i[1][0]}({i[1][1]}) - {i[2][0]}({i[2][1]}) - {i[3][0]}({i[3][1]}) источник:{i[1][2]}\n'
        else:
            s += f'{i[0]}\n'
    temp_user_data.temp_data(user_id)[user_id][4] = copy.deepcopy([])
    temp_user_data.temp_data(user_id)[user_id][0] = status
    cleaner()
    bot.send_message(user_id, s)


def get_all_ratio(user_id):
    status = temp_user_data.temp_data(user_id)[user_id][0]
    selected_team = temp_user_data.temp_data(user_id)[user_id][3]
    sport = temp_user_data.temp_data(user_id)[user_id][1]
    temp_user_data.temp_data(user_id)[user_id][0] = 2
    bot.send_message(user_id, 'Выполняется поиск поиск матча на ТОП БК...')
    threading.Thread(target=LigaStavok, args=(selected_team, temp_user_data, user_id)).start()# work all
    threading.Thread(target=FonBet, args=(sport, selected_team, temp_user_data, user_id)).start()  # work all
    threading.Thread(target=OlimpBet, args=(sport, selected_team, temp_user_data, user_id)).start()# work all
    threading.Thread(target=Pari, args=(sport, selected_team, temp_user_data, user_id)).start() # work all
    threading.Thread(target=Leon, args=(selected_team, temp_user_data, user_id)).start()
    threading.Thread(target=waiter, args=(user_id, status)).start()


def main():
    @bot.message_handler(commands=['start', 'admin'])
    def start_msg(message):
        name_user = message.from_user.first_name
        user_id = message.from_user.id
        buttons = Bot_inline_btns()
        command = message.text.replace('/', '')
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        if command == 'start':
            bot.send_message(message.chat.id, 'Сравни кэфы БК, чтобы ставочка зашла выгоднее\nНапиши название команды из'
                                              ' хоккея, футбола или баскетбола, а я выдам коэффициенты среди топовых БК\n* '
                                              'Pari\n* BetBoom\n* БэтСити\n* FonBet\n* Leon\n* Winline\n* OlimpBet\n* Лига ставок',
                             reply_markup=buttons.start_btns(), parse_mode="HTML")
        elif db_actions.user_is_admin(user_id):
            if command == 'admin':
                bot.send_message(message.chat.id, f'{message.from_user.first_name}, вы успешно вошли в Админ-Панель ✅',
                                 reply_markup=buttons.admin_btns())

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            code = temp_user_data.temp_data(user_id)[user_id][0]
            if command[:5] == 'sport':
                print(command[1:])
                temp_user_data.temp_data(user_id)[user_id][0] = 0
                temp_user_data.temp_data(user_id)[user_id][1] = command[5:]
                print(temp_user_data.temp_data(user_id)[user_id][1])
                bot.send_message(user_id, 'Напиши название команды')
            elif command[:4] == 'game' and code == 1:
                temp_user_data.temp_data(user_id)[user_id][3] = temp_user_data.temp_data(user_id)[user_id][2][int(command[4:])]
                get_all_ratio(user_id)
            if db_actions.user_is_admin(user_id):
                if command == 'export':
                    db_actions.db_export_xlsx()
                    bot.send_document(call.message.chat.id, open(config.get_config()['xlsx_path'], 'rb'))
                    os.remove(config.get_config()['xlsx_path'])

    @bot.message_handler(content_types=['text', 'photo'])
    def text_message(message):
        photo = message.photo
        user_input = message.text
        user_id = message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            code = temp_user_data.temp_data(user_id)[user_id][0]
            match code:
                case 0:
                    if user_input is not None:
                        strict_data = db_actions.get_team_matches_strict(temp_user_data.temp_data(user_id)[user_id][1], user_input)
                        print(strict_data)
                        if len(strict_data) > 0:
                            if len(strict_data) == 1:
                                temp_user_data.temp_data(user_id)[user_id][0] = None
                                temp_user_data.temp_data(user_id)[user_id][3] = strict_data[0]
                                get_all_ratio(user_id)
                            else:
                                temp_user_data.temp_data(user_id)[user_id][2] = strict_data
                                temp_user_data.temp_data(user_id)[user_id][0] = 1
                                bot.send_message(user_id, f'Для этой команды нашлось {len(strict_data)} матча: ',
                                                 reply_markup=buttons.games_btns(strict_data))
                        else:
                            full_data = db_actions.get_team_matches(temp_user_data.temp_data(user_id)[user_id][1], user_input)
                            print(full_data)
                            if len(full_data) > 0:
                                if len(full_data) == 1:
                                    temp_user_data.temp_data(user_id)[user_id][0] = None
                                    temp_user_data.temp_data(user_id)[user_id][3] = full_data[0]
                                    get_all_ratio(user_id)
                                else:
                                    temp_user_data.temp_data(user_id)[user_id][2] = full_data
                                    temp_user_data.temp_data(user_id)[user_id][0] = 1
                                    bot.send_message(user_id, 'По твоему запросу нашлось больше одной команды: ',
                                                     reply_markup=buttons.games_btns(full_data))
                            else:
                                bot.send_message(user_id, 'По твоему запросу не нашлось команд, попробуй ещё раз')
                    else:
                        bot.send_message(user_id, 'Это не текст!')

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    threading.Thread(target=schedule_worker).start()
    schedule.every().day.at('00:00').do(sync_db)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
