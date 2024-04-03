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
        assortiment = types.InlineKeyboardButton('Футбол', callback_data='sportfootball')
        cart = types.InlineKeyboardButton('Хоккей', callback_data='sporthockey')
        bonus = types.InlineKeyboardButton('Баскетбол', callback_data='sportbasketball')
        self.__markup.add(assortiment, cart, bonus)
        return self.__markup

    def admin_btns(self):
        export = types.InlineKeyboardButton('Экспорт БД', callback_data='export')
        self.__markup.add(export)
        return self.__markup

    def games_btns(self, games):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, g in enumerate(games):
            print(g)
            btn = types.InlineKeyboardButton(f'{g[1]} - {g[2]} * {g[0] }', callback_data=f'game{i}')
            markup.add(btn)
        return markup