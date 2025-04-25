from project import db
from project import app
from project.models.post import Post
from project.models.user import User
with app.app_context():
    db.drop_all()
    db.create_all()
    # Создание пользователя
    user = User(username='john', email='john@example.com', password='123456')

    # Создание поста
    post = Post(title='First Post', content='Hello World!', author=user)

    # Добавление в базу
    db.session.add(user)
    db.session.add(post)
    db.session.commit()


    print(User.query.all())