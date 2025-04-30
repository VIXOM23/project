from . import app, db
from .models import User
with app.app_context():
    print(User.query.all())
