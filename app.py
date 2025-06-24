from flask import Flask, render_template, request, redirect, url_for, g
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
import sqlite3
import os
from datetime import datetime


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['DATABASE'] = os.path.join(basedir, 'instance', 'posts.db')
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


login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, name, email, password, bio=None, avatar=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.bio = bio
        self.avatar = avatar

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, email, password, bio, avatar FROM user WHERE id = \"{user_id}\"")
    user_data = cursor.fetchone()
    if user_data:
        return User(*user_data)
    return None


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


@app.context_processor
def inject_app_config():
    return dict(app=app)


def init_db():
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'upload', 'posts'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'upload', 'avatars'), exist_ok=True)
    
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Создаем таблицы, если они не существуют
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                bio TEXT,
                avatar TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                content TEXT NOT NULL,
                image TEXT,
                date TEXT NOT NULL,
                reading_time INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES user (id)
            )
        """)
        
        db.commit()
        
        # Проверяем, есть ли пользователи
        cursor.execute("SELECT COUNT(*) FROM user")
        if cursor.fetchone()[0] == 0:
            # Добавляем тестовых пользователей
            test_users = [
                ("Иван Иванов", "ivan@example.com", "secure123", "Профессор математики", "avatar.png"),
                ("Мария Петрова", "maria@example.com", "secure456", "Исследователь в области алгебры", "avatar.png")
            ]
            for user in test_users:
                cursor.executemany(f"""
                    INSERT INTO user (name, email, password, bio, avatar)
                    VALUES (\"{user[0]}\", \"{user[1]}\", \"{user[2]}\", \"{user[3]}\", \"{user[0]}\")
                """)
                db.commit()
            print("Created test users")

        # Проверяем, есть ли посты
        cursor.execute("SELECT COUNT(*) FROM post")
        if cursor.fetchone()[0] == 0:
            # Получаем ID пользователей
            cursor.execute("SELECT id FROM user")
            user_ids = [row[0] for row in cursor.fetchall()]
            
            if user_ids:
                test_posts = [
                    ('Теория вероятностей', 'Основные концепции теории вероятностей...', 
                     '<p>F</p>', 'upload/posts/post.jpg', '15 июня 2023', 8, user_ids[0]),
                    ('Линейная алгебра', 'A', '<p>Основные понятия линейной алгебры...</p>', 
                     None, '10 июня 2023', 12, user_ids[0]),
                    ('Дифференциальные уравнения', 'Методы решения ДУ...', 
                     '<p>Разбираем основные методы...</p>', None, '5 июня 2023', 10, user_ids[1])
                ]
                for post in test_posts:
                    cursor.executemany(f"""
                        INSERT INTO post (title, excerpt, content, image, date, reading_time, author_id)
                        VALUES (\"{post[0]}\", \"{post[0]}\", \"{post[0]}\", \"{post[0]}\", \"{post[0]}\", \"{post[0]}\", \"{post[0]}\")
                    """)
                    db.commit()
                print("Created test posts")
            else:
                print("No users found to assign posts to")


@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.*, u.name as author_name, u.avatar as author_avatar
        FROM post p
        JOIN user u ON p.author_id = u.id
        ORDER BY p.date DESC
    """)
    posts = cursor.fetchall()
    return render_template('index.html', posts=posts, current_user=current_user)


@app.route('/post/<int:post_id>')
def post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"""
        SELECT p.*, u.name as author_name, u.avatar as author_avatar, u.bio as author_bio
        FROM post p
        JOIN user u ON p.author_id = u.id
        WHERE p.id = {post_id}
    """)
    post_item = cursor.fetchone()
    if not post_item:
        return "Post not found", 404
    return render_template('post.html', post=post_item)


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    db = get_db()
    cursor = db.cursor()
    
    # Получаем данные пользователя
    cursor.execute(f"SELECT * FROM user WHERE id = \"{user_id}\"")
    user_data = cursor.fetchone()
    if not user_data:
        return "User not found", 404
    
    user = User(*user_data)
    
    # Получаем посты пользователя
    cursor.execute(f"""
        SELECT * FROM post 
        WHERE author_id = {user_id}
        ORDER BY date DESC
    """)
    posts = cursor.fetchall()
    
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

            db = get_db()
            cursor = db.cursor()
            
            # Проверяем, существует ли email
            cursor.execute(f"SELECT id FROM user WHERE email = \"{email}\"")
            if cursor.fetchone():
                return render_template('registration.html', 
                                     error="Email уже используется",
                                     form_data={
                                        'username': username,
                                        'email': email,
                                        'bio': bio
                                    })

            filepath = app.config['DEFAULT_AVATAR']

            if avatar and avatar.filename != '':
                filepath = f"upload/avatars/{avatar.filename}"
                avatar.save(os.path.join(app.root_path, 'static', filepath))

            # Добавляем нового пользователя
            cursor.execute(f"""
                INSERT INTO user (name, email, password, bio, avatar)
                VALUES (\"{username}\", \"{email}\", \"{password}\", \"{bio}\", \"{filepath}\")
            """)
            db.commit()

            return redirect(url_for('login'))
            
        except Exception as e:
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

            db = get_db()
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM user WHERE email = \"{email}\"")
            user_data = cursor.fetchone()
            
            if not user_data:
                return error_login_redir()
            
            if user_data['password'] != password:
                return error_login_redir()
            
            user = User(*user_data)
            login_user(user, remember=True)

            return redirect(url_for('index'))

        except Exception as e:
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
        title = request.form['title']
        excerpt = request.form['excerpt']
        content = request.form['content']
        reading_time = int(request.form['reading_time'])
        image_file = request.files.get('image')
        
        if len(title) > 50 or len(excerpt) > 150:
            return "Превышена максимальная длина поля", 400
        
        image_path = None
        if image_file and image_file.filename != '':
            filename = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}"
            filepath = os.path.join('upload', 'posts', filename)
            os.makedirs(os.path.join(app.root_path, 'static', 'upload', 'posts'), exist_ok=True)
            image_file.save(os.path.join(app.root_path, 'static', filepath))
            image_path = filepath
        
        today = datetime.now()
        date_str = f"{today.day} {MONTHS_RU[today.month]} {today.year}"
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"""
            INSERT INTO post (title, excerpt, content, image, date, reading_time, author_id)
            VALUES (\"{title}\", \"{excerpt}\", \"{content}\", \"{image_path}\", \"{date_str}\", \"{reading_time}\", \"{current_user.id}\")
        """)
        db.commit()
        
        return redirect(url_for('user_profile', user_id=current_user.id))
    
    except Exception as e:
        return f"Ошибка при создании поста: {str(e)}", 500


if __name__ == '__main__':
    init_db() 
    app.run(debug=True, host='0.0.0.0', port=5000)
    
