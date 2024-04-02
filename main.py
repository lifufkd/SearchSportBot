#####################################
#            Created by             #
#               SBR                 #
#####################################
config_name = 'secrets.json'
#####################################
import os
import telebot
import platform
from threading import Lock
from parser import ConfigParser, AllMatches
from frontend import Bot_inline_btns
from backend import TempUserData, DbAct
from db import DB
#####################################


def second_phase(user_id):
    team_correct_name = temp_user_data.temp_data(user_id)[user_id][3]
    parser_obj = temp_user_data.temp_data(user_id)[user_id][4]
    data = parser_obj.second_phase(team_correct_name)
    print(data)
    del parser_obj

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
                temp_user_data.temp_data(user_id)[user_id][0] = 0
                temp_user_data.temp_data(user_id)[user_id][1] = command[5:]
                bot.send_message(user_id, 'Напиши название команды')
            elif command[:4] == 'team' and code == 1:
                temp_user_data.temp_data(user_id)[user_id][3] = temp_user_data.temp_data(user_id)[user_id][2][command[4:]]
                second_phase(user_id)
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
                        parser = AllMatches()
                        parser.init()
                        status = parser.first_phase(user_input)
                        match status[0]:
                            case 0:
                                bot.send_message(user_id, 'Такая команда не найдена, попробуйте ввести ещё раз')
                            case 1:
                                temp_user_data.temp_data(user_id)[user_id][2] = status[1]
                                temp_user_data.temp_data(user_id)[user_id][0] = 1
                                bot.send_message(user_id, 'По твоему запросу нашлось больше одной команды: ', reply_markup=buttons.teams_btns(status[1]))
                            case 2:
                                temp_user_data.temp_data(user_id)[user_id][0] = None
                                temp_user_data.temp_data(user_id)[user_id][3] = user_input
                                temp_user_data.temp_data(user_id)[user_id][4] = parser
                                second_phase(user_id)
                        del parser
                    else:
                        bot.send_message(user_id, 'Это не текст!')
                case 1:
                    if photo is not None:
                        photo_id = photo[-1].file_id
                        photo_file = bot.get_file(photo_id)
                        photo_bytes = bot.download_file(photo_file.file_path)
                        temp_user_data.temp_data(user_id)[user_id][1][1] = photo_bytes
                        temp_user_data.temp_data(user_id)[user_id][0] = 2
                        bot.send_message(user_id, 'Отправьте описание товара')
                    else:
                        bot.send_message(user_id, 'Это не фото!')
                case 2:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][2] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 3
                        categories = db_actions.get_categories()
                        bot.send_message(user_id, 'Выберите категорию для товара',
                                         reply_markup=buttons.categories_btns(categories))
                    else:
                        bot.send_message(user_id, 'Это не текст!')
                case 4:
                    if user_input is not None:
                        db_actions.add_category(user_input)
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, 'Категория успешно добавлена!')
                    else:
                        bot.send_message(user_id, 'Это не текст!')
                case 6:
                    if user_input is not None:
                        db_actions.update_product('name', user_input, temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, 'Товар успешно обновлён!')
                    else:
                        bot.send_message(user_id, 'Это не текст!')
                case 7:
                    if user_input is not None:
                        db_actions.update_product('description', user_input,
                                                  temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, 'Товар успешно обновлён!')
                    else:
                        bot.send_message(user_id, 'Это не текст!')
                case 8:
                    if photo is not None:
                        photo_id = photo[-1].file_id
                        photo_file = bot.get_file(photo_id)
                        photo_bytes = bot.download_file(photo_file.file_path)
                        db_actions.update_product('photo', photo_bytes, temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, 'Товар успешно обновлён!')
                    else:
                        bot.send_message(user_id, 'Это не фото!')

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
