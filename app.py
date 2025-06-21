from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'posts.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(70))
    avatar = db.Column(db.String(100))
    posts = db.relationship('Post', backref='author', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    excerpt = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))
    date = db.Column(db.String(50), nullable=False)
    reading_time = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def init_db():
    if not os.path.exists(os.path.join(basedir, 'instance')):
        os.makedirs(os.path.join(basedir, 'instance'))
    
    with app.app_context():
        db.create_all()
        
        # Создаем тестового пользователя если его нет
        if not User.query.first():
            test_users = [
                User(
                    name="Иван Иванов",
                    email="ivan@example.com",
                    password="secure123",
                    bio="Профессор математики",
                    avatar="avatar.png"
                ),
                User(
                    name="Мария Петрова",
                    email="maria@example.com",
                    password="secure456",
                    bio="Исследователь в области алгебры",
                    avatar="avatar.png"
                )
            ]
            db.session.bulk_save_objects(test_users)
            db.session.commit()
            print("Created test users")

        # Создаем тестовые посты если их нет
        if not Post.query.first():
            users = User.query.all()
            if users:
                test_posts = [
                    Post(
                        title='Теория вероятностей',
                        excerpt='Основные концепции теории вероятностей...',
                        content="""
                        <p>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                        FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                        FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                        FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF</p>
                        """,
                        image='post.jpg',
                        date='15 июня 2023',
                        reading_time=8,
                        author_id=users[0].id
                    ),
                    Post(
                        title='Линейная алгебра',
                        excerpt="""
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        """,
                        content='<p>Основные понятия линейной алгебры...</p>',
                        image=None,
                        date='10 июня 2023',
                        reading_time=12,
                        author_id=users[0].id
                    ),
                    Post(
                        title='Дифференциальные уравнения',
                        excerpt='Методы решения ДУ...',
                        content='<p>Разбираем основные методы...</p>',
                        image=None,
                        date='5 июня 2023',
                        reading_time=10,
                        author_id=users[1].id
                    )
                ]
                db.session.bulk_save_objects(test_posts)
                db.session.commit()
                print("Created test posts")
            else:
                print("No users found to assign posts to")


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def post(post_id):
    post_item = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post_item)


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            bio = request.form['bio']
            avatar = request.files['avatar']

            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return render_template('registration.html', 
                                     error="Email уже используется",
                                     form_data={
                                        'username': username,
                                        'email': email,
                                        'bio': bio
                                    })

            filepath = None

            if avatar:
                if avatar.filename != '': filepath = f"upload/{avatar.filename}"

            new_user = User(
                name=username,
                email=email,
                password=password,
                bio=bio,
                avatar=filepath
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}", 500
            
    return render_template('registration.html')


@app.route('/login')
def login():
    return render_template('registration.html')


if __name__ == '__main__':
    init_db() 
    app.run(debug=True) #  host='0.0.0.0', port=5000


    
