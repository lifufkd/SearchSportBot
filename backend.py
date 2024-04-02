#####################################
#            Created by             #
#               zzsxd               #
#               SBR                 #
#####################################
import os
import time
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, [], None, None]})
        return self.__user_data


class DbAct:
    def __init__(self, db, config, path_xlsx):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__fields = ['Имя', 'Фамилия', 'Никнейм']
        self.__dump_path_xlsx = path_xlsx

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write(
                'INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin, shoping_cart) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, first_name, last_name, nick_name, is_admin, json.dumps([])))

    def user_is_existed(self, user_id):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def user_is_admin(self, user_id):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def add_product(self, data):
        self.__db.db_write('INSERT INTO product (name, photo, description, categori_id) VALUES (?, ?, ?, ?)', data)

    def products_by_id_category(self, categori_id):
        return self.__db.db_read('SELECT row_id, name, description, photo FROM product WHERE categori_id = ?', (categori_id, ))

    def add_category(self, name):
        self.__db.db_write('INSERT INTO category (name) VALUES (?)', (name, ))

    def get_categories(self):
        return self.__db.db_read('SELECT row_id, name FROM category', ())

    def del_categories(self, categori_id):
        self.__db.db_write('DELETE FROM category WHERE categori_id = ?', (categori_id, ))

    def get_products_preview(self):
        return self.__db.db_read('SELECT row_id, name FROM product', ())

    def update_product(self, field, data, row_id):
        self.__db.db_write(f'UPDATE product SET "{field}" = ? WHERE row_id = ?', (data, row_id))

    def get_product_by_id(self, product_id):
        return self.__db.db_read('SELECT name FROM product WHERE row_id = ?', (product_id, ))[0]

    def get_shipping_cart_by_user_id(self, user_id):
        data = self.__db.db_read('SELECT shoping_cart FROM users WHERE user_id = ?', (user_id,))[0][0]
        print(data)
        return json.loads(data)

    def update_shipping_cart(self, user_id, product_id):
        already_in_json = self.__db.db_read('SELECT shoping_cart FROM users WHERE user_id = ?', (user_id, ))[0][0]
        already_in = json.loads(already_in_json)
        if product_id in already_in:
            return False
        else:
            already_in.append(product_id)
            new_json = json.dumps(already_in)
            self.__db.db_write(f'UPDATE users SET shoping_cart = ? WHERE user_id = ?', (new_json, user_id))
            return True


    def db_export_xlsx(self):
        d = {'Имя': [], 'Фамилия': [], 'Никнейм': []}
        users = self.__db.db_read('SELECT first_name, last_name, nick_name FROM users', ())
        if len(users) > 0:
            for user in users:
                for info in range(len(list(user))):
                    d[self.__fields[info]].append(user[info])
            df = pd.DataFrame(d)
            df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='пользователи', index=False)
