from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from project1.models import Admin, User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirmpassword = PasswordField("Confirm Password", validators=[
                                    DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is taken. Выбери другое")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is taken. Выбери другое")


class LoginFrom(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log In")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField("Обновить фото профиля", validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")

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
