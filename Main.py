import datetime, os, time
from functions import *
from flask import url_for, request, render_template, redirect, session
from constant import *
from flask_sqlalchemy import sqlalchemy
from database import *


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', title='Главная страница')
    if request.method == 'POST':
        if request.form.get('search'):
            questions_search = []
            questions = db.session.query(Memequestion).all()
            for question in questions:
                if request.form.get('search') in [x for x in question.title.split() if len(x) > 3]:
                    questions_search.append(question)
            return render_template('questions.html', title='Вопросы', questions=questions, user_check=user_check,
                                   Memeuser=Memeuser, db=db, )


@app.route('/questions/<int:id_category>', methods=['GET', 'POST'])
def questions(id_category=1):
    if id_category == 1:
        questions = db.session.query(Memequestion).all()
    else:
        questions = db.session.query(Memequestion).filter_by(id_category=id_category).all()
    if request.method == 'GET':
        return render_template('questions.html', title='Вопросы', questions=questions, user_check=user_check,
                               Memeuser=Memeuser, db=db, )
    if request.method == 'POST':
        pass


@app.route('/question/<int:id_question>', methods=['GET', 'POST'])
def question(id_question=1):
    answers = db.session.query(Memeanswer).filter_by(id_question=id_question).all()
    question = db.session.query(Memequestion).filter_by(id=id_question).first()
    if request.method == 'GET':
        return render_template('question.html', title='Вопрос', question=question, user_check=user_check,
                               answers=answers,
                               Memeuser=Memeuser, db=db, category=db.session.query(Memecategory))
    if request.method == 'POST':

        if request.form.get('text'):
            answer = Memeanswer(id_user=session['user_id'], id_question=id_question, text=request.form.get('text'))
            db.session.add(answer)
            db.session.commit()
    return render_template('question.html', title='Вопрос', question=question, user_check=user_check,
                           Memeuser=Memeuser, db=db, answers=answers, category=db.session.query(Memecategory))


@app.route('/delete_question/<int:id_question>', methods=['GET', 'POST'])
def delete_question(id_question=1):
    try:
        if 'user_id' not in session:
            return redirect('/error')
        question = db.session.query(Memequestion).filter_by(id=id_question).first()
        answers = db.session.query(Memeanswer).filter_by(id=id_question).all()

        for i in answers:
            db.session.delete(i)
        db.session.delete(question)
        db.session.commit()
        return redirect('/profile')
    except Exception:
        return redirect('/error')


@app.route('/delete_answer/<int:id_question>/<int:id_answer>', methods=['GET', 'POST'])
def delete_answer(id_question=1, id_answer=1):
    try:
        if 'user_id' not in session:
            return redirect('/error')
        answer = db.session.query(Memeanswer).filter_by(id=id_answer, id_question=id_question).first()
        db.session.delete(answer)
        db.session.commit()
        return redirect('/profile')
    except Exception:
        return redirect('/error')


@app.route('/delete_user/<int:id_user>', methods=['GET', 'POST'])
def delete_user(id_user):
    try:
        if 'user_id' not in session:
            return redirect('/error')
        if not db.session.query(Admins).filter_by(id_user=session['user_id']).first():
            return redirect('/error')

        question = db.session.query(Memequestion).filter_by(id_user=id_user).first()
        answers = db.session.query(Memeanswer).filter_by(id_user=id_user).all()
        user = db.session.query(Memeuser).filter_by(id=id_user).first()
        for i in answers:
            db.session.delete(i)
        db.session.delete(question)
        db.session.delete(user)

        db.session.commit()
        return redirect('/admin')
    except Exception:
        return redirect('/error')


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

    if 'user_id' not in session:
        return redirect('/error')

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
            return redirect('/question/{}'.format(question.id))
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
            session.clear()
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


@app.route('/error')
def error():
    return render_template('error.html', title='Информация')


@app.route('/infocompany')
def infocompany():
    return render_template('infocompany.html', title='Информация')


@app.route('/regulation')
def regulation():
    return render_template('regulation.html', title='Правила')


@app.route('/help')
def help():
    return render_template('help.html', title='Помощь')


@app.route('/admin')
def admin_console():
    if 'user_id' not in session:
        return redirect('/error')
    if not db.session.query(Admins).filter_by(id_user=session['user_id']).first():
        return redirect('/error')
    users = db.session.query(Memeuser).all()
    return render_template('admin.html', title='Админ', users=users)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/error')
    user_model = user_check(session['user_id'], db, Memeuser)
    questions = db.session.query(Memequestion).filter_by(id_user=user_model.id).all()
    answers = db.session.query(Memeanswer).filter_by(id_user=user_model.id).all()

    if request.method == 'GET':
        return render_template('profile.html', title='Профиль', user_model=user_model, questions=questions,
                               category=db.session.query(Memecategory), answers=answers)
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
            if request.files.get('file').mimetype.split('/')[1] in IMAGE_RESOLUTION:
                filename = 'static/{}'.format(user_model.id) + '/image_.' + \
                           request.files.get('file').mimetype.split('/')[1]
            else:
                text += 'Это разрешение не поддерживается'
                return render_template('profile.html', title='Профиль', text=text, incorrect=incorrect,
                                       user_model=user_model, category=db.session.query(Memecategory))
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
                               user_model=user_model, category=db.session.query(Memecategory))


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
