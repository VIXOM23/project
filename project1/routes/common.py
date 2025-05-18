from os import error
from Demos.win32ts_logoff_disconnected import username
from flask import redirect, render_template, request_started, url_for, flash, request, Blueprint
from project1.forms import (RegistrationForm, LoginFrom, UpdateAccountForm)
from project1 import app, db, mail
from project1.models import User, Admin
from flask_login import login_user, current_user, logout_user, login_required, login_url
from flask_mail import Message
from .utils import save_picture, validate_image_file
common_bp = Blueprint('common', __name__)


@common_bp.route("/")
@login_required
def home():
    return render_template("main.html", title="Домашняя страница")



@common_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    return render_template("personal_account.html", title='Account')


@common_bp.route('/account/edit', methods = ["GET", "POST"])
@login_required
def edit_account_info():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        
        if current_user.get_role() == 'user':
            user = User.query.get(current_user.id)
        elif current_user.get_role() == 'admin':
            user = Admin.query.get(current_user.id)

        file = form.avatar.data
        if file:
            user.set_image(file) #pyright: ignore
        user.username = form.username.data  # pyright: ignore
        user.email = form.email.data  # pyright: ignore
        if form.password.data != "":
            user.set_password(form.confirm_password.data) #pyright:ignore
        db.session.commit()

        return redirect(url_for("common.account"))

    if request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username
    return render_template('edit_account.html', title="Изменение данных аккаунта", form = form)

@common_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('common.home'))


@common_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('common.login'))
    return render_template('registration.html', title='Register', form=form)


@common_bp.route('/login', methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('common.home'))

    form = LoginFrom()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user: 
            if user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
            
                return redirect(next_page) if next_page else redirect(url_for('common.home'))
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin:
            if admin.check_password(form.password.data):
                login_user(admin)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('common.home'))
    return render_template('login.html', title='login', form=form)

@common_bp.route("/upload")
@login_required
def upload():
    if current_user.get_role() == 'admin':
        return redirect(url_for('common.home'))
    if current_user.lasts <= 0:
        return redirect("sub.shop")
    user = User.query.get(current_user.id)
    user.lasts = user.lasts - 1
    db.session.commit()
    return redirect(url_for('common.home'))


