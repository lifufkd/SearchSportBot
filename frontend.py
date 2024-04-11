#####################################
#            Created by             #
#               zzsxd               #
#####################################
import telebot
from telebot import types


#####################################


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_btns(self):
        assortiment = types.InlineKeyboardButton('Футбол ⚽️', callback_data='sportfootball')
        cart = types.InlineKeyboardButton('Хоккей🏒 ', callback_data='sporthockey')
        bonus = types.InlineKeyboardButton('Баскетбол 🏀', callback_data='sportbasketball')
        self.__markup.add(assortiment, cart, bonus)
        return self.__markup

    def new_btns(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        assortiment = types.KeyboardButton('Футбол ⚽️')
        cart = types.KeyboardButton('Хоккей🏒')
        bonus = types.KeyboardButton('Баскетбол 🏀')
        keyboard.add(assortiment, cart, bonus)
        return keyboard

    def admin_btns(self):
        btn1 = types.InlineKeyboardButton('обновить частые команды', callback_data='update_often_teams')
        #export = types.InlineKeyboardButton('Экспорт БД', callback_data='export')
        self.__markup.add(btn1)
        return self.__markup

    def games_btns(self, games):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in range(games):
            btn = types.InlineKeyboardButton(f'{i+1}', callback_data=f'game{i}')
            markup.add(btn)
        btn = types.InlineKeyboardButton(f'Найти другую команду', callback_data=f'gameВыбрать спорт')
        markup.add(btn)
        return markup