from . import app, db
from .models.user import User
with app.app_context():
    print(User.query.all())
