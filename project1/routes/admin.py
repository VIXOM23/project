from flask import redirect, render_template, url_for, request, Blueprint, abort
from project1.forms import UpdateUserInfo, UserFilterForm
from project1 import db
from project1.models import Sub, User
from flask_login import current_user, login_required

from project1.routes.utils import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/settings', methods=["GET"])
@login_required
@admin_required
def settings():
    return render_template('admin/admin_panel.html', title='Настройки') 





@admin_bp.route('/settings/subs', methods=["GET", "POST"])
@login_required
def sub_settings(): 
    if current_user.get_role() != 'admin':
        abort(403)
    sub1, sub2, sub3  = Sub.query.all()
    
    if request.method == "POST":
        print('args:', request.args)
    return render_template('admin/subscription_settings.html', title="Настройки подписки ", sub1 = sub1, sub2= sub2, sub3 = sub3)

@admin_bp.route('/user_settings', methods=["GET", "POST"])
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
        elif search_type == 'has_access':
            users = User.query.filter(User.lasts > 0)
    return render_template('admin/user_settings.html', users = users, title="Настройки пользователей", form=form)


@admin_bp.route('/user_pages/<int:user_id>', methods=["GET", "POST"])
@login_required
def user_pages(user_id):
    if current_user.get_role() != 'admin':
        abort(403)
    form = UpdateUserInfo()
    user = User.query.get_or_404(user_id)
    if form.validate_on_submit():
        user = User.query.get(int(user_id))
        user.lasts = form.lasts.data
        user.date_end = form.date_end.data
        user.is_blocked = form.is_blocked.data
        db.session.commit()
        return redirect(url_for('admin.user_settings', user_id = user_id))
    if request.method == "GET":
        form.date_end.data = user.date_end
        form.is_blocked.data = user.is_blocked
        form.lasts.data = user.lasts
    return render_template('admin/user_profile.html',
                           title="Страница пользователя",
                           user=user,
                           form = form)
