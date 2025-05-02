from project1.models import Admin, User
from project1 import app, db

with app.app_context():

    admin = Admin(username = "Admin1",
                  email = "karpenkov.2005@mail.ru")
    admin.set_password("password1")
    db.session.add(admin)
    db.session.commit()
