from project1.models import User
from project1 import app, db

with app.app_context():
    db.drop_all()
    db.create_all()
