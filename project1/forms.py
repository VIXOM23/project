from flask import Flask
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
import wtforms
from flask_login import current_user
from wtforms import DateField, IntegerField, RadioField, StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError, email

from project1.models import Admin, User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirmpassword = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is taken. Выбери другое")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is taken. Выбери другое")


class UpdateUserInfo(FlaskForm):
    date_end = DateField("Конец пользования подписки", validators=[Optional()])
    is_blocked = BooleanField("Заблокировать")
    lasts = IntegerField("Оставшиеся попытки")
    submit = SubmitField("Подтвердить изменения")


    def validate_lasts(self, lasts):
        if lasts.data >= 10:
            raise ValidationError("Количество разрешенных доступов слишком большое")



class LoginFrom(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

    
    def validate_login(self, email):
        user = User.query.filter_by(email=self.email.data).first()
        admin = Admin.query.filter_by(email = self.email.data).first()

        if not user and not admin:
            raise ValidationError("Пользователь с таким логином не найден")

    def validate_password(self, password):
        user = User.query.filter_by(email=self.email.data).first()
        admin = Admin.query.filter_by(email = self.email.data).first()

        if user:
 
            if not user.check_password(self.password.data):
                raise ValidationError("Неправильный логин или пароль!")
        elif admin:
            if not admin.check_password(self.password.data):
                raise ValidationError("Неправильный логин или пароль!")


class UserFilterForm(FlaskForm):
    search_type = RadioField("Тип поиска", 
                             choices=[
                                ('username', 'Логин'),
                                ('username_soft', 'Частичное совпадение по логину'),
                                ('email', 'Почта'),
                                ('email_soft', 'Частичное совпадение по почте'),
                                ('subscribe', 'Активная подписка'),
                                ('has_access', 'Имеющие доступ к сервису'),
                                ('blocked', 'Заблокированные'),
                
                             ])
    search_query = StringField("Запрос", render_kw={"placeholder": "Введите значение для поиска"})
    submit = SubmitField("Искать")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[
                           DataRequired(), Length(min=2, max=20)],
                          render_kw={"placeholder": "USERNAME", "class": "account-input"})
    email = StringField("Email", validators=[DataRequired(), Email()],
                         render_kw={"placeholder": "EMAIL ADDRESS", "class": "account-input"})
    password = StringField("PASSWORD", validators=[],
                           render_kw={"placeholder": "YOUR PASSWORD", "class": "account-input",
                                      "type" : "password"})
    confirm_password = StringField("CONFIRM PASsWORD", validators=[],
                                  render_kw={"placeholder": "NEW PASSWORD", "class": "account-input", 
                                             "type" : "password"})
    submit = SubmitField("Apply Chandes",
                         render_kw={'class': 'account-button'})
    
    def validate_password(self, password):
        if self.password.data != "":
            if not current_user.check_password(self.password.data): 
                raise ValidationError("Неверный пароль")


    def validate_username(self, username):
        
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username is taken. Выбери другое")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email is taken. Выбери другое")

class SearchUsers(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    submit = SubmitField("Искать")

    def validate_login(self, login):
        user=User.query.filter_by(username=login.data).first()
        if user is None:
            raise ValidationError("Такого пользователя нет")


class RequestResetFrom(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Запросить смену пароля")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        admin= Admin.query.filter_by(email=email.data).first()
        if user is None and admin is None:
            raise ValidationError("Такого аккаунта нет")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")


class UpdateSubForm(FlaskForm):
    title = StringField("Название подписки", validators=[Optional()])
    duration_days = IntegerField("Дни", render_kw={'class': 'plan-input plan-number'}, validators=[Optional()])
    duration_month = IntegerField("Месяцы", render_kw={'class': 'plan-input plan-number'}, validators=[Optional()])
    duration_year = IntegerField("Годы", render_kw={'class': 'plan-input plan-number'}, validators=[Optional()])
    cost1 = IntegerField("Стоимость", render_kw={'class': 'plan-input price-number'}, validators=[Optional()])
    cost2 = IntegerField("Стоимость", render_kw={'class': 'plan-input price-number'}, validators=[Optional()])
    cost3 = IntegerField("Стоимость", render_kw={'class': 'plan-input price-number'}, validators=[Optional()])

    submit = SubmitField("Apply changes", render_kw={'class': 'account-button apply-button'})


    def validate_days(self, duration_days):
        if self.duration_days.data >= 31 or self.duration_days.data < 0:
            raise ValidationError("Неверное количество дней")

    
    def validate_month(self, duration_month):
        if self.duration_month.data >= 12 or self.duration_month.data < 0:
            raise ValidationError("Неверное количество месяцев") 


    def validate_year(self, duration_year):
        if self.duration_year.data < 0:
            raise ValidationError("Количество лет не может быть отрицательным")

    def validate_cost(self, cost1):
        if self.cost1.data < 0:
            raise ValidationError("Стоимость не может быть отрицательной")
        
    def validate_cost(self, cost2):
        if self.cost2.data < 0:
            raise ValidationError("Стоимость не может быть отрицательной")

    def validate_cost(self, cost3):
        if self.cost3.data < 0:
            raise ValidationError("Стоимость не может быть отрицательной")          
    
