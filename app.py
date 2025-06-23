from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'posts.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'idi_nahui'
app.config['DEFAULT_AVATAR'] = 'default/__MATHUB__DEFAULT__AVATAR__AANG__.png'

MONTHS_RU = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_app_config():
    return dict(app=app)


class User(UserMixin, db.Model):
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
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

    os.makedirs(os.path.join(app.root_path, 'static', 'upload', 'posts'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'upload', 'avatars'), exist_ok=True)
    
    # ... остальной код инициализации ...
    
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
                        image='upload/posts/post.jpg',
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
    return render_template('index.html', posts=posts, current_user=current_user)


@app.route('/post/<int:post_id>')
def post(post_id):
    post_item = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post_item)


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(author_id=user.id).all()
    return render_template('user_profile.html', user=user, posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
                if avatar.filename != '': 
                    filepath = f"upload/avatar/{avatar.filename}"
                    avatar.save(f"static/avatar/{filepath}")
            else:
                filepath = app.config['DEFAULT_AVATAR']

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


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            def error_login_redir():
                return render_template('login.html', 
                                     error="Неверный email или пароль",
                                     form_data={
                                        'email': email
                                    })

            required_user = User.query.filter_by(email=email).first()
            if not required_user:
                return error_login_redir()
            
            elif required_user.password != password:
                return error_login_redir()
            
            login_user(required_user, remember=True)

            posts = Post.query.all()

            return render_template(
                'index.html', posts=posts,
                current_user=current_user)

        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}", 500


    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    try:
        # Получение данных из формы
        title = request.form['title']
        excerpt = request.form['excerpt']
        content = request.form['content']
        reading_time = int(request.form['reading_time'])
        image_file = request.files.get('image')
        
        # Валидация данных
        if len(title) > 50 or len(excerpt) > 150:
            return "Превышена максимальная длина поля", 400
        
        # Обработка изображения
        image_path = None
        if image_file and image_file.filename != '':
            filename = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}"
            filepath = os.path.join('upload', 'posts', filename)
            os.makedirs(os.path.join(app.root_path, 'static', 'upload', 'posts'), exist_ok=True)
            image_file.save(os.path.join(app.root_path, 'static', filepath))
            image_path = filepath
        
        # Форматирование даты
        today = datetime.now()
        date_str = f"{today.day} {MONTHS_RU[today.month]} {today.year}"
        
        # Создание нового поста
        new_post = Post(
            title=title,
            excerpt=excerpt,
            content=content,
            image=image_path,
            date=date_str,
            reading_time=reading_time,
            author_id=current_user.id
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return redirect(url_for('user_profile', user_id=current_user.id))
    
    except Exception as e:
        db.session.rollback()
        return f"Ошибка при создании поста: {str(e)}", 500


if __name__ == '__main__':
    init_db() 
    app.run(
            debug=True,
            host='0.0.0.0',
            port=5000
            ) #  host='0.0.0.0', port=5000
