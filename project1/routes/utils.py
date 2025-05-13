from functools import wraps
import os
from flask import abort
import secrets
from PIL import Image
from flask_login import current_user
from .. import app, mail
from flask_mail import Message
from flask import url_for

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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset', sender="noreply@gmail.com",
                  recipients=[user.email])
    msg.body = f'''
    Чтобы обновить свой пароль перейди по ссылке:
    {url_for('help.reset_token', token=token, _external=True)}
    '''
    mail.send(msg)


def validate_image_file(image_filename):
    _, _, ext = image_filename.partition(".")
    print(image_filename.partition(":"), "FILENAME")
    if ext not in ("jpg, png"):
        return False
    return True

# Декоратор для роутов, которые требуют админа
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.get_role() != "admin":
            abort(403)
        return func(*args, **kwargs)
    return decorated_view
