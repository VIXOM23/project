from project import app, db
from project.models.user import User
with app.app_context():
    print(User.query.all())
