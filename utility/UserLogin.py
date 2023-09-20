from flask import url_for

class UserLogin():
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getNName(self):
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
        pass
