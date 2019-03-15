import datetime, os, time

from flask import url_for, request, render_template, redirect, session

from database import *

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', title='Главная страница')
    if request.method == 'POST':
        pass


@app.route('/questions/<int:category_id>', methods=['GET', 'POST'])
def questions(category_id):
    if request.method == 'GET':
        questions = db.session.query(Memequestion).filter_by(id=category_id).first()
        return render_template('questions.html', title='Главная страница')
    if request.method == 'POST':
        pass


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html', title='Регистрация')
    elif request.method == 'POST':
        try:
            password = request.form.get('inputPassword')
            user_name = request.form.get('inputUserName')
            email = request.form.get('inputEmail')
            sex = request.form.get('sex')
            user = Memeuser(email=email,
                            name=user_name,
                            sex=sex,
                            password=password,
                            point=100,
                            photo=url_for('static', filename='image.jpg'))

            db.session.add(user)
            db.session.commit()
            newpath = r'C:\Users\ilyam\PycharmProjects\MemeSite\static\{}\\'.format(user.id)
            if not os.path.exists(newpath):
                os.makedirs(newpath)

        except sqlalchemy.exc.IntegrityError:
            return render_template('registration.html', title='Регистрация',
                                   text="Возможно вы уже зарегистрировали на эту почту"
                                        " аккаунт или ваше имя уже используется")

        return redirect('/login')


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    text = ''
    if request.method == 'GET':
        return render_template('add_question.html', title='Добавить вопрос')
    if request.method == 'POST':
        if 0 < int(request.form.get('point')) < 500 and request.form.get('text') and request.form.get('title'):
            title = request.form.get('title')
            text = request.form.get('text')
            points = int(request.form.get('point'))
            user_model = db.session.query(Memeuser).filter_by(id=session['user_id']).first()
            id_category = db.session.query(Memecategory).filter_by(category=request.form.get('category')).first().id
            question = Memequestion(id_user=user_model.id,
                                    title=title,
                                    text=text,
                                    point=points,
                                    active=True,
                            id_category=id_category)

            if int(user_model.point) < points:
                text += 'Недостаточно pointов'
                return render_template('add_question.html', title='Добавить вопрос', text=text)

            user_model.point -= points

            db.session.add(question)
            db.session.commit()
        else:
            text += 'Проверьте правильность введённых данных'
            return render_template('add_question.html', title='Добавить вопрос', text=text)
        return render_template('question.html', title='Вопрос', text=text)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Авторизация')
    elif request.method == 'POST':
        email = request.form.get('inputEmail')
        password = request.form.get('inputPassword')
        user_model = db.session.query(Memeuser).filter_by(email=email).first()
        if user_model and user_model.password == password:

            session['username'] = user_model.name
            session['user_id'] = user_model.id
            return redirect('/profile')
        else:
            return render_template('login.html', title='Авторизация', text='Введите корректные данные')


@app.route('/leaders')
def leaders():
    leaders = Memeuser.query.all()
    leaders_list = []

    for leader in leaders:
        leaders_list.append((leader.name, int(leader.point)))

    return render_template('leaders.html', title='Лидеры',
                           leaders=sorted(leaders_list, key=lambda x: x[1], reverse=True), enumerate=enumerate)


@app.route('/infocompany')
def infocompany():
    return render_template('infocompany.html', title='Информация')


@app.route('/regulation')
def regulation():
    return render_template('regulation.html', title='Правила')


@app.route('/help')
def help():
    return render_template('help.html', title='Помощь')


# @app.route('/admin')
# def admin():
#     user_n = list(filter((lambda x: x[1] != 'admin'), (list(map((lambda x: (x[0], x[1])), users.get_all())))))
#     news_n = [(x[0], len(news.get_all(x[0]))) for x in user_n]
#
#     return render_template('admin.html', title='Авторизация', users=user_n, news=news_n, len=len)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_model = db.session.query(Memeuser).filter_by(id=session['user_id']).first()
    if request.method == 'GET':
        return render_template('profile.html', title='Профиль', user_model=user_model)
    elif request.method == 'POST':
        text = ''
        incorrect = False

        if request.form.get('NewName'):
            user_model.name = request.form.get('NewName')
            db.session.commit()
            session['username'] = user_model.name

        if request.form.get('NewEmail'):
            user_model.email = request.form.get('NewEmail')
            db.session.commit()
        if request.form.get('NewPassword') and request.form.get('OldPassword') == user_model.password:
            user_model.password = request.form.get('NewPassword')
            db.session.commit()

        if request.files.get('file'):
            filename = 'static/{}'.format(user_model.id) + '/image_.' + \
                       request.files.get('file').mimetype.split('/')[1]
            print(filename)
            user_model.photo = filename

            db.session.commit()
            with open(r"C:\Users\ilyam\PycharmProjects\MemeSite\static\{}\{}".format(user_model.id, '/image_.' +
                                                                                                    request.files.get(
                                                                                                        'file').mimetype.split(
                                                                                                        '/')[1]),
                      'wb') as photo:
                photo.write(request.files.get('file').read())

        else:
            text = 'Введите корректные данные'
            incorrect = True

        return render_template('profile.html', title='Профиль', text=text, incorrect=incorrect,
                               user_model=user_model)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


# @app.route('/add_news', methods=['GET', 'POST'])
# def add_news():
#     if 'username' not in session:
#         return redirect('/login')
#     form = AddNewsForm()
#     if form.validate_on_submit():
#         title = form.title.data
#         content = form.content.data
#         nm = NewsModel(db.get_connection())
#
#         nm.insert(title, content, session['user_id'],
#                   (time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())[:10]))
#         return redirect("/index")
#     return render_template('add_question.html', title='Добавление новости',
#                            form=form, username=session['username'])
#
#
# @app.route('/delete_news/<int:news_id>', methods=['GET'])
# def delete_news(news_id):
#     if 'username' not in session:
#         return redirect('/login')
#     nm = NewsModel(db.get_connection())
#     nm.delete(news_id)
#     return redirect("/index")


if __name__ == '__main__':
    app.run(port=8070, host='127.0.0.1')
