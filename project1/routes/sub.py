from flask import render_template, Blueprint, abort

from project1 import db
from project1.models import Sub
from project1.forms import UpdateSubForm
from flask_login import current_user, login_required


sub_bp = Blueprint('sub', __name__)


@sub_bp.route('/subs-shop', methods = ["GET", "POST"])
@login_required
def subs_shop():
    sub1, sub2, sub3  = Sub.query.all()
    return render_template("user_subscription.html", 
                           title = "Подписка",
                           sub1 = sub1,
                           sub2 = sub2,
                           sub3 = sub3)

@sub_bp.route('/settings/subs/sub_<int:sub_id>', methods=["GET", "POST"])
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
