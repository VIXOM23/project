from logging import log
from random import choice
from Demos.win32ts_logoff_disconnected import username
from PIL import Image
import os
import secrets
from flask import redirect, render_template, url_for, flash, request, abort
from wtforms.validators import email
from project1.forms import (RegistrationForm, LoginFrom, UpdateAccountForm,
                            RequestResetFrom, ResetPasswordForm, SearchUsers, UpdateSubForm, UserFilterForm,
                            UpdateUserInfo)
from project1 import app, db, bcrypt, mail
from project1.models import Sub, User, Admin
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@login_required
def home():
    return render_template("main.html", title="Домашняя страница")


@app.route('/settings', methods=["GET"])
@login_required
def settings():
    if current_user.get_role() != 'admin':
        abort(403)
    return render_template('admin/settings.html', title='Настройки') 


@app.route('/settings/subs/sub_<int:sub_id>', methods=["GET", "POST"])
@login_required
def sub_page(sub_id):
    if current_user.get_role() != 'admin':
        abort(403)

    sub = Sub.query.get(sub_id)
    form = UpdateSubForm()
    if form.validate_on_submit():
        sub.title = form.title.data
        sub.duration_days = form.duration_days.data
        sub.duration_months = form.duration_month.data
        sub.duration_years = form.duration_year.data
        sub.cost = form.cost.data
        db.session.commit()
    return render_template('admin/sub_page.html', title="Подписка",
                           sub = sub,
                           form = form)

@app.route('/settings/subs', methods=["GET", "POST"])
@login_required
def sub_settings():
    if current_user.get_role() != 'admin':
        abort(403)
    subs = Sub.query.all()
    return render_template('admin/sub_settings.html', title="Настройки подписки ", subs=subs)

#TODO: Добавить в модель USER поле активные попытки
@app.route('/user_settings', methods=["GET", "POST"])
@login_required
def user_settings():
    if current_user.get_role() != 'admin':
        abort(403)

    users = None   
    form = UserFilterForm()
    if form.validate_on_submit():
        search_type = form.search_type.data
        search_query = form.search_query.data
        if search_type == 'username':
            users = User.query.filter_by(username = search_query)
        elif search_type == 'username_soft':
            users = User.query.filter(User.username.contains(search_query)).all()
        elif search_type == 'email':
            users = User.query.filter_by(email=search_query)
        elif search_type == 'email_soft':
            users = User.query.filter(User.email.contains(search_query))
        elif search_type == 'subscribe':
            users = User.query.filter(User.date_end.isnot(None)).all()
        elif search_type == 'blocked':
            users = User.query.filter_by(is_blocked = True) 
    return render_template('admin/user_settings.html', users = users, title="Настройки пользователей", form=form)


@app.route('/user_pages/<int:user_id>', methods=["GET", "POST"])
@login_required
def user_pages(user_id):
    if current_user.get_role() != 'admin':
        abort(403)
    form = UpdateUserInfo()
    user = User.query.get(user_id)
    if form.validate_on_submit():
        user = User.query.get(int(user_id))
        user.date_end = form.date_end.data
        user.is_blocked = form.is_blocked.data
        db.session.commit()
        return redirect(url_for('user_pages', user_id = user_id))
    if request.method == "GET":
        form.date_end.data = user.date_end
        form.is_blocked.data = user.is_blocked
        form.lasts.data = 5
    return render_template('admin/user_profile.html',
                           title="Страница пользователя",
                           user=user,
                           form = form)



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
                    login_user(user)
                    next_page = request.args.get('next')
                
                    return redirect(next_page) if next_page else redirect(url_for('home'))
            admin = Admin.query.filter_by(email=form.email.data).first()
            if admin:
                if admin.check_password(form.password.data):
                    login_user(admin)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('home'))
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
        flash(f"Аккаунт создан для {form.username.data},{form.email.data}", 'success')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)


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
    output_size = (256, 256)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn



@app.route('/subs-shop', methods = ["GET", "POST"])
@login_required
def subs_shop():

    return "<h1>Страница магазина подписок</h1>"

@app.route('/account/edit', methods = ["GET", "POST"])
@login_required
def edit_account_info():
    return "<h1> Обновление аккаунта </h1>"


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    # form = UpdateAccountForm()
    # if form.validate_on_submit():
    #     if current_user.get_role() == 'user':
    #         user = User.query.get(current_user.id)
    #         if form.picture.data:
    #             picture_file = save_picture(form.picture.data)
    #             user.image_file = picture_file  # pyright: ignore
    #         user.username = form.username.data  # pyright: ignore
    #         user.email = form.email.data  # pyright: ignore
    #         db.session.commit()
    #         flash("Аккаунт обновлён!", "success")
    #         return redirect(url_for("account"))
    #     elif current_user.get_role() == 'admin':
    #
    #         user = Admin.query.get(current_user.id)
    #         if form.picture.data:
    #             picture_file = save_picture(form.picture.data)
    #             user.image_file = picture_file  # pyright: ignore
    #         user.username = form.username.data  # pyright: ignore
    #         user.email = form.email.data  # pyright: ignore
    #         db.session.commit()
    #         flash("Аккаунт обновлён!", "success")
    #         return redirect(url_for("account"))
    #
    # elif request.method == "GET":
    #     form.username.data = current_user.username
    #     form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template("personal_account.html", title='Account', image_file=image_file)


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
