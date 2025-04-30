from .. import app, db
from ..models import Admin, User
with app.app_context():
    # admin = Admin(username="Mihail",
    #               email="karpenkov.2004@mail.ru")
    # admin.set_password("MyAssasin2004")
    # db.session.add(admin)
    # db.session.commit()
    print(Admin.query.all())
    print(User.query.all())
