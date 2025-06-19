from flask import Flask, render_template

app = Flask(__name__)

# Плейсхолдеры
posts = [
    {
        'id': 1,
        'title': 'Теория вероятностей',
        'excerpt': 'text1',
        'image': 'post1.jpg',
        'date': '12 мая 2023',
        'reading_time': 5,
        'content': '<p>text2</p>'
    },
    {
        'id': 2,
        'title': 'Линейная алгебра',
        'excerpt': 'text3',
        'image': None,
        'date': '8 мая 2023',
        'reading_time': 7,
        'content': '<p>text4</p>'
    },
    {
        'id': 3,
        'title': 'Дифференциальные уравнения',
        'excerpt': 'text5.',
        'image': 'post2.jpg',
        'date': '3 мая 2023',
        'reading_time': 4,
        'content': '<p>text6</p>'
    }
]


@app.route('/')
def index():
    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def post(post_id):
    post_item = next((post for post in posts if post['id'] == post_id), None)
    return render_template('post.html', post=post_item)


if __name__ == '__main__':
    app.run(debug=True)
