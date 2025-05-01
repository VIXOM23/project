from Demos.win32ts_logoff_disconnected import username
from PIL import Image
import os
import secrets
from flask import redirect, render_template, url_for, flash, request, abort
from wtforms.validators import email
from project1.forms import (RegistrationForm, LoginFrom, UpdateAccountForm,
                            RequestResetFrom, ResetPasswordForm, SearchUsers)
from project1 import app, db, bcrypt, mail
from project1.models import User, Admin
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@login_required
def home():
    return render_template("homepage.html", title="Домашняя страница")


@app.route('/settings', methods=["GET"])
@login_required
def settings():
    if current_user.get_role() != 'admin':
        abort(403)
    return render_template('admin/settings.html', title='Настройки') 




@app.route('/user_settings', methods=["GET", "POST"])
@login_required
def user_settings():
    form = SearchUsers()
    all_users = request.args.get('all_users', 0, type=int)
    users = None
    if all_users:
        users = User.query.all()
    if current_user.get_role() != 'admin':
        abort(403)
    finded_user = None
    if form.validate_on_submit():
        finded_user = User.query.filter_by(username = form.login.data).first()
    return render_template('admin/user_settings.html',
                           title='Настройки пользователей',
                           users = users,
                           form = form,
                           finded_user = finded_user)
    

@app.route('/sub_settings', methods=["GET"])
@login_required
def sub_settings():
    if current_user.get_role() != 'admin':
        abort(403)
    return render_template('admin/sub_settings.html', title='Настройки пользователей')

@app.route('/about')
def about():
    return "<h1>Welcome to about page<h1>"


@app.route('/login', methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginFrom()
    if form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if user.check_password(form.password.data):
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                
                    return redirect(next_page) if next_page else redirect(url_for('home'))
            user = Admin.query.filter_by(email=form.email.data).first()
            if user:
                if user.check_password(form.password.data):
                    login_user(user, remember=form.remember.data)
            flash("Неправильный логин или пароль", 'danger')
    return render_template('login.html', title='login', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,  # pyright: ignore
                    email=form.email.data) # pyright: ignore
        user.set_password(form.password.data) 

        with app.app_context():
            db.session.add(user)
            db.session.commit()
        flash(f"Аккаунт создан для {form.username.data}, {
              form.email.data}", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

#TODO: Поменять смену информации для админов, возможно сделать функцию для получения пользователя 
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    form = UpdateAccountForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file  # pyright: ignore
        # Обновляем данные без app_context (он уже есть)
        user.username = form.username.data  # pyright: ignore
        user.email = form.email.data  # pyright: ignore
        db.session.commit()
        flash("Аккаунт обновлён!", "success")
        return redirect(url_for("account"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title='Account', image_file=image_file, form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset', sender="noreply@gmail.com",
                  recipients=[user.email])
    msg.body = f'''
    Чтобы обновить свой пароль перейди по ссылке:
    {url_for('reset_token', token=token, _external=True)}
    '''
    mail.send(msg)


@app.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetFrom()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Письмо было отправлено', 'info')
            send_reset_email(user)
            return redirect(url_for('login'))
        user = Admin.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Письмо было отправлено', 'info')
            return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@login_required
@app.route('/subscribition')
def sub():
    return render_template('sub.html')
    

@app.route('/reset_password/<string:token>', methods=["GET", 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Неправильный или просроченный токен", 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Пароль был успешно обновлен")
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
