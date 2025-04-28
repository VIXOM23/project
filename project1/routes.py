from Demos.win32ts_logoff_disconnected import username
from PIL import Image
import os
import secrets
from flask import redirect, render_template, url_for, flash, request, abort
from project1.forms import PostForm, RegistrationForm, LoginFrom, UpdateAccountForm, PostForm
from project1 import app, db, bcrypt
from project1.models.user import User
from project1.models.post import Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template("homepage.html", title="Домашняя страница", posts=posts)


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
        user = User(username=form.username.data,  # pyright: ignore
                    email=form.email.data,  # pyright: ignore
                    password=hashed_password)  # pyright: ignore

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


@app.route("/post/new", methods=['GET', "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,  # pyright: ignore
                    content=form.content.data,  # pyright: ignore
                    author=current_user)  # pyright: ignore
        db.session.add(post)
        db.session.commit()
        flash("Пост был создан", 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form,
                           legend="New Post")


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Твой пост был обновлен", 'success')
        return redirect(url_for('post', post_id=post.id))

    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html",
                           title="Update Post", form=form,
                           legend="Update Post")


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Пост был успешно удален", "success")
    return redirect(url_for("home"))
