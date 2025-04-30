from project1.models import Admin, User
from project1 import app, db

with app.app_context():
    for i in range(20):
        user = User(username=f'User:{i}',
                    email=f'{i}@mail.ru')
        user.set_password(f'password{i}')
        db.session.add(user)
    admin = Admin(username = "Admin",
                  email = "karpenkov.2004@mail.ru")
    admin.set_password("password1")
    db.session.add(admin)
    db.session.commit()
