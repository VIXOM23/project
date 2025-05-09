from datetime import date, datetime
from enum import unique
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import Nullable
from sqlalchemy.sql.functions import user
from project1 import db, login_manager, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    user_type, _, user_id = user_id.partition(":")
    if user_type == "user":
        return User.query.get(int(user_id))
    elif user_type == "admin":
        return Admin.query.get(int(user_id))
    return None

class BaseUser(UserMixin):

    def get_role(self):
        return self.__class__.__name__.lower()

class User(BaseUser, db.Model):

    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date_started = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    lasts = db.Column(db.Integer, default = 5)
    is_blocked = db.Column(db.Boolean(), nullable=False, default=False)


    def is_active(self):
        return self.date_end != None
    
    def get_id(self):
        return f"user:{self.id}"

    
    def int_id(self):
        return self.id


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.get_id()})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])

        user_id = s.loads(token, 30)['user_id']
        user_type, _, user_id = user_id.partition(":")
        if user_type == "user":
            return User.query.get(int(user_id))
        elif user_type == "admin":
            return Admin.query.get(int(user_id))

        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Admin(BaseUser, db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')


    def get_id(self):
        return f"admin:{self.id}"


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.get_id()})

    #TODO: Переписать всю эту лабуду
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:

            user_id = s.loads(token, 1800)['user_id']
        except:
            return None
        return Admin.query.get(user_id)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}', '{self.image_file}')"


class Sub(db.Model):
    __tablename__ = 'Sub'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable = False, unique=True)
    duration_days = db.Column(db.Integer, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    duration_years = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    

    def __repr__(self) -> str:
        return f"Sub({self.title}, {self.duration_years} лет, {self.duration_months} месяцев, {self.duration_days} дней, {self.cost})"
