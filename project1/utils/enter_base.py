from project1.models import Admin, User, Sub
from project1 import app, db

with app.app_context():

    for i in range(10):
        user = User(username=f"User:{i}", 
                    email = f"{i}@mail.ru")
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
    for i in range(10):
        user = User(username=f"AnotherUser:{i}",
                    email = f"another{i}@mail.ru")
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

    admin=Admin(username = "Admin",
                email="admin@mail.ru")
    admin.set_password('password')
    db.session.add(admin)
    db.session.commit()

    sub1 = Sub(title = '1',
               duration_days = 1, 
               duration_months = 0, 
               duration_years= 2,
               cost = 10)


    sub2 = Sub(title ='2',
               duration_days = 2, 
               duration_months = 2, 
               duration_years= 2,
               cost = 10)
   
    sub3 = Sub(title = '3',
               duration_days = 1, 
               duration_months = 1, 
               duration_years = 1,
               cost = 10)
    db.session.add(sub1)
    db.session.commit()
    db.session.add(sub2)
    db.session.commit()
    db.session.add(sub3)
    db.session.commit()
