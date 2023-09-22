import sqlite3
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session, g,
                   current_app)

admin = Blueprint('admin', __name__,
                  template_folder='templates',
                  static_folder='static')


def login_admin():
    session['admin_logged'] = 1


def isLogged():
    return True if session.get('admin_logged') else False


def logout_admin():
    session.pop('admin_logged', None)


db = None
@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    db = g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.logout', 'title': 'Выйти'},
        {'url': '.list_pubs', 'title': 'Список статей'}]

@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))
    return render_template('admin/index.html',
                           menu=menu,
                           title='Админ-панель')


@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        data = request.form.to_dict()
        if data['user'] == "admin" and data['psw'] == "123456":
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")
    return render_template('admin/login.html', title="Админ-панель")


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()
    return redirect(url_for('.login'))

@admin.route('/list-pubs')
def list_pubs():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД "+str(e))

    return render_template('admin/listpubs.html',
                            title='Список статей',
                            menu=menu,
                            list=list)
