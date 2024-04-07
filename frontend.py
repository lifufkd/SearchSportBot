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

    def admin_btns(self):
        export = types.InlineKeyboardButton('Экспорт БД', callback_data='export')
        self.__markup.add(export)
        return self.__markup

    def games_btns(self, games):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in range(games):
            btn = types.InlineKeyboardButton(f'{i+1}', callback_data=f'game{i}')
            markup.add(btn)
        return markup

    def new_search_btns(self, stat):
        markup = types.InlineKeyboardMarkup(row_width=1)
        d1 = types.InlineKeyboardButton('Выбрать другой матч по той же команде', callback_data='new_search1')
        d2 = types.InlineKeyboardButton('Найти матчи другой команды', callback_data='new_search2')
        if stat:
            markup.add(d1, d2)
        else:
            markup.add(d2)
        return markup