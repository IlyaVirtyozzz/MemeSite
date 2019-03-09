from flask import Flask, url_for, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy

import time, datetime
from operator import itemgetter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Memeuser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    sex = db.Column(db.String(10), unique=True, nullable=False)
    point = db.Column(db.Integer, primary_key=True, nullable=False)
    def __repr__(self):
        return '<YandexLyceumStudent {} {} {} {} {}>'.format(
            self.id, self.name, self.email, self.password, self.sex)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html', title='Регистрация')
    elif request.method == 'POST':

        password = request.form['inputPassword']
        user_name = request.form.get('inputUserName')
        email = request.form.get('inputEmail')
        sex = request.form.get('sex')
        user = Memeuser(email=email,
                        name=user_name,
                        sex=sex,
                        password=password,
                        point=100
                        )
        db.session.add(user)
        db.session.commit()
        return


@app.route('/infocompany')
def infocompany():
    return render_template('infocompany.html', title='Информация')


@app.route('/regulation')
def regulation():
    return render_template('regulation.html', title='Правила')


@app.route('/help')
def help():
    return render_template('help.html', title='Помощь')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Авторизация')
    elif request.method == 'POST':
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]) and user_name == 'admin' and password == 'admin':
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect("/admin")
        elif (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect("/index")
        else:
            return redirect("/register")


@app.route('/admin')
def admin():
    user_n = list(filter((lambda x: x[1] != 'admin'), (list(map((lambda x: (x[0], x[1])), users.get_all())))))
    news_n = [(x[0], len(news.get_all(x[0]))) for x in user_n]

    return render_template('admin.html', title='Авторизация', users=user_n, news=news_n, len=len)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')

    news = sorted(NewsModel(db.get_connection()).get_all(session['user_id']),
                  key=lambda x: (x[1], datetime.datetime.strptime(x[4], '%Y-%m-%d')))

    print(news)
    return render_template('index.html', username=session['username'],
                           news=news)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        nm = NewsModel(db.get_connection())

        nm.insert(title, content, session['user_id'],
                  (time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())[:10]))
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.3')
