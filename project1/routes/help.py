from flask import redirect, render_template, url_for, flash, Blueprint
from project1.forms import RequestResetFrom, ResetPasswordForm
from project1 import db, bcrypt
from project1.models import User, Admin
from flask_login import current_user, login_required
from .utils import send_reset_email

help_bp = Blueprint('help', __name__)

@help_bp.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetFrom()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Письмо было отправлено', 'info')
            send_reset_email(user)
            return redirect(url_for('common.login'))
        user = Admin.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Письмо было отправлено', 'info')
            return redirect(url_for('common.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@login_required
@help_bp.route('/subscribition')
def sub():
    return render_template('sub.html')
    
#TODO: Сделать лучше
@help_bp.route('/reset_password/<string:token>', methods=["GET", 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    print(user)
    admin = Admin.verify_reset_token(token)
    print(admin)
    if user is None and admin is None:
        flash("Неправильный или просроченный токен", 'warning')
        return redirect(url_for('help.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            return redirect(url_for('common.login'))
        if admin:
            admin.set_password(form.password.data)
            db.session.commit()
            return redirect(url_for('common.login'))

    return render_template('reset_token.html', title='Reset Password', form=form)
