from flask import url_for
from flask_login import UserMixin

class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        if self.__user:
            return self.__user['name']
        return "Без имени"

    def getEmail(self):
        if self.__user:
            return self.__user['email']
        return "Без email"

    def getAvatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path +
                                       url_for('static',filename='images/default.png'),
                                       "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию "+str(e))
        else:
            img = self.__user['avatar']

        return img

    def verifyExt(self, filename):
        # frmt = filename.rsplit('.', 1)[1]
        # if frmt == 'png' or frmt == 'PNG':
        #     return True
        # return False
        if filename.endswith('.png') or filename.endswith('.PNG'):
            return True
        return False
