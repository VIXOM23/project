from Demos.win32ts_logoff_disconnected import username
from flask import redirect, render_template, url_for, flash
from project.forms import RegistrationForm, LoginFrom
from project import app, db, bcrypt
from project.models.user import User
from project.models.post import Post


@app.route("/")
@app.route("/home")
def home():
    return render_template("homepage.html", title="Домашняя страница")

@app.route('/about')
def about():
    return "<h1>Welcome to about page<h1>"

@app.route('/login', methods = ["GET", "POST"])
def login():
    form = LoginFrom()
    if form.validate_on_submit():
        flash(f"You logged in as user {form.email.data}", 'success')
    return render_template('login.html', title = 'login', form = form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        with app.app_context():
            db.session.add(user)
            db.session.commit()
        flash(f"Аккаунт создан для {form.username.data}, {form.email.data}", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

