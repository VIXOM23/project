from Demos.win32ts_logoff_disconnected import username
import os
import secrets
from flask import redirect, render_template, url_for, flash, request
from project1.forms import RegistrationForm, LoginFrom, UpdateAccountForm
from project1 import app, db, bcrypt
from project1.models.user import User
from project1.models.post import Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template("homepage.html", title="Домашняя страница")


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
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')

                return redirect(next_page) if next_page else redirect(url_for('home'))
            flash("Не получилось войти", 'danger')
    return render_template('login.html', title='login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)

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
    form_picture.save(picture_path)
    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    form = UpdateAccountForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        # Обновляем данные без app_context (он уже есть)
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash("Аккаунт обновлён!", "success")
        return redirect(url_for("account"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title='Account', image_file=image_file, form=form)
