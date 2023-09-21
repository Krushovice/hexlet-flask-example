import sqlite3
import os

from database.db import FDataBase
from utility.forms import LoginForm, RegisterForm
from utility.UserLogin import UserLogin
from utility.validate import validate_post

from flask import (Flask, flash, render_template, request,
                   redirect, url_for, get_flashed_messages,
                   make_response, session, abort, g)

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (LoginManager, login_user,
                         login_required, current_user, logout_user)


# конфигурация
SECRET_KEY = "3&t72u%*23a$59#1f%8hs*$%hre#@%"
DEBUG = True
DATABASE = '/tmp/database/flsite.db'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,
                                             'database/flstite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'log_in'
login_manager.login_message = """Для просмотра данной страницы,
необходимо авторизоваться"""

login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    # Вспомогательная функция для создания таблиц БД
    db = connect_db()
    with app.open_resource('database/sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase

    db = get_db()
    dbase = FDataBase(db)


@app.route('/')
def index():
    return render_template('index.html',
                           menu=dbase.getMenu(),
                           posts=dbase.getPostsAnnounce())


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/page404.html',
                           title='Страница не найдена')


@app.errorhandler(401)
def denied_access(error):
    return render_template('errors/page401.html',
                           title='Неавторизованный пользователь')


# @app.route('/about')
# def about():
#     return render_template('about.html',
#                            title='О сайте',
#                            menu=menu)


@app.route("/add_post", methods=["POST", "GET"])
def add_post():

    if request.method == "POST":
        name = request.form['name']
        post = request.form['post']
        url = request.form['url']
        if validate_post(name, post):
            res = dbase.addPost(name, post, url)
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка.Увеличьте количество символов',
                  category='error')

    return render_template('posts/add_post.html',
                           menu=dbase.getMenu(),
                           title="Добавление статьи")


@app.route("/post/<alias>")
@login_required
def show_post(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('posts/post.html', menu=dbase.getMenu(),
                           title=title,
                           post=post)


# @app.route('/contact', methods=['GET', 'POST'])
# def contact():

#     if request.method == "POST":
#         if len(request.form['username']) > 2:
#             flash('Сообщение отправлено', category='success')
#         else:
#             flash('Ошибка отправки', category="error")
#     return render_template('contact.html',
#                            title="Обратная связь",
#                            menu=dbase.getMenu())


@app.route('/profile')
@login_required
def profile():

    return render_template('users/profile.html',
                           menu=dbase.getMenu(),
                           title="Профиль")


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)

        if user and check_password_hash(user['psw'], form.psw.data):
            user_log = UserLogin().create(user)
            rm = form.remember.data
            login_user(user_log, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Неверная пара логин/пароль', 'error')

    return render_template('login.html',
                           title='Авторизация',
                           menu=dbase.getMenu(),
                           form=form)


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    answr = make_response(img)
    answr.headers['Content-Type'] = 'image/png'
    return answr


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        verify = current_user.verifyExt(file.filename)
        if file and verify:
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка добавления автара", "error")
                flash("Аватар обновлен", "success")

            except FileNotFoundError as e:
                print("Ошибка чтения файла "+str(e))
                flash("Ошибка чтения файла", "error")

        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for("profile"))


@app.route('/logout')
@login_required
def log_out():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('log_in'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash('Вы успешно зарегистрированы', 'success')
            return redirect(url_for('log_in'))
        else:
            flash('Ошибка добавления в БД', 'error')

    return render_template('register.html',
                           title='Регистрация',
                           menu=dbase.getMenu(),
                           form=form)


if __name__ == '__main__':
    app.run(debug=True)
