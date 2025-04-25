from project1 import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', back_populates='author')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
