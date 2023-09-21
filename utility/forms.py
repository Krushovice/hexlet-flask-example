from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = SearchField("Email: ", validators=[Email()])
    psw = PasswordField("Пароль: ", validators=[DataRequired()])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")
