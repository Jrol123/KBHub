from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'posts.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))
    date = db.Column(db.String(50), nullable=False)
    reading_time = db.Column(db.Integer, nullable=False)


def init_db():
    if not os.path.exists(os.path.join(basedir, 'instance')):
        os.makedirs(os.path.join(basedir, 'instance'))
    
    with app.app_context():
        db.create_all()
        if not Post.query.first():
            initial_posts = [
                Post(
                    title='Теория вероятностей',
                    excerpt='Исследование основных концепций теории вероятностей...',
                    content='<p>Полное содержание поста о теории вероятностей...</p>',
                    image=None,
                    date='12 мая 2023',
                    reading_time=5
                ),
                Post(
                    title='Линейная алгебра',
                    excerpt='Основы линейной алгебры: от векторов и матриц...',
                    content='<p>Полное содержание поста о линейной алгебре...</p>',
                    image=None,
                    date='8 мая 2023',
                    reading_time=7
                ),
                Post(
                    title='Дифференциальные уравнения',
                    excerpt='Методы решения обыкновенных дифференциальных уравнений...',
                    content='<p>Полное содержание поста о диффурах...</p>',
                    image='post.jpg',
                    date='3 мая 2023',
                    reading_time=4
                )
            ]
            db.session.bulk_save_objects(initial_posts)
            db.session.commit()


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def post(post_id):
    post_item = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post_item)


if __name__ == '__main__':
    init_db() 
    app.run(host='0.0.0.0', port=5000)
