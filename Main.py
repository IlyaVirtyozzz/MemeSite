import os
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Авторизация')
    elif request.method == 'POST':
        if login_func(request.form.get('inputEmail'), request.form.get('inputPassword'), session):
            return redirect('/profile')
        else:
            return render_template('login.html', title='Авторизация', text='Введите корректные данные')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html', title='Регистрация')
    elif request.method == 'POST':
        try:
            user = add_new_user(request.form.get('inputEmail'), request.form.get('inputUserName'),
                                request.form.get('sex'), request.form.get('inputPassword'))


        except sqlalchemy.exc.IntegrityError:
            return render_template('registration.html', title='Регистрация',
                                   text="Возможно вы уже зарегистрировали на эту почту"
                                        " аккаунт или ваше имя уже используется")

        return redirect('/login')


@app.route('/questions/<int:id_category>/<int:active>', methods=['GET', 'POST'])
def questions(id_category=1, active=1):
    questions = filter_questions(id_category, active)
    if request.method == 'GET':
        return render_template('questions.html', title='Вопросы', questions=questions, user_check=user_check,
                               Memeuser=Memeuser, db=db, session=session, is_admin=is_admin)


@app.route('/true_answer/<int:id_question>/<int:id_answer>', methods=['GET', 'POST'])
def true_answer(id_question, id_answer):
    try:
        true_answer_func(id_question, id_answer, session)
        return redirect("/question/{}".format(id_question))
    except Exception:
        return redirect('/error')


@app.route('/question/<int:id_question>', methods=['GET', 'POST'])
def question(id_question):
    try:
        answers = db.session.query(Memeanswer).filter_by(id_question=id_question).all()
        question = db.session.query(Memequestion).filter_by(id=id_question).first()
        if request.method == 'GET':
            return render_template('question.html', title='Вопрос', question=question, user_check=user_check,
                                   answers=answers,
                                   Memeuser=Memeuser, db=db, category=db.session.query(Memecategory), session=session,
                                   is_admin=is_admin)
        if request.method == 'POST':
            if request.form.get('text'):
                add_answer_func(session, id_question, request.form.get('text'), 0)
            return redirect('/question/{}'.format(id_question))
        return render_template('question.html', title='Вопрос', question=question, user_check=user_check,
                               Memeuser=Memeuser, db=db, answers=answers, category=db.session.query(Memecategory),
                               session=session)
    except Exception:
        return redirect('/error')


@app.route('/close_question/<int:id_question>', methods=['GET', 'POST'])
def close_question(id_question):
    try:
        if 'user_id' not in session:
            return redirect('/error')
        if not is_user_question(id_question, session["user_id"]):
            return redirect('/error')
        close_question_func(id_question)
        return redirect('/profile')
    except Exception:
        return redirect('/error')


@app.route('/delete_question/<int:id_question>', methods=['GET', 'POST'])
def delete_question(id_question):
    try:
        if 'user_id' not in session:
            return redirect('/error')

        if not (is_user_question(id_question, session["user_id"]) or is_admin(session)):
            return redirect('/error')
        if not delete_question_func(id_question):
            return redirect('/error')

        return redirect('/profile')
    except Exception:
        return redirect('/error')


@app.route('/delete_answer/<int:id_question>/<int:id_answer>', methods=['GET', 'POST'])
def delete_answer(id_question, id_answer):
    try:
        if 'user_id' not in session:
            return redirect('/error')

        if not (is_user_answer(id_question, id_answer, session['user_id']) or is_admin(session)):
            return redirect('/error')

        if not delete_answer_func(id_question, id_answer):
            return redirect('/error')

        return redirect('/profile')
    except Exception:
        return redirect('/error')


@app.route('/delete_user/<int:id_user>', methods=['GET', 'POST'])
def delete_user(id_user):
    try:
        if 'user_id' not in session:
            return redirect('/error')
        if not is_admin(session):
            return redirect('/error')
        if session['user_id'] == id_user:
            return redirect('/error')
        if not delete_user_func(id_user):
            return redirect('/error')

        return redirect('/admin')
    except Exception:
        return redirect('/error')


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    try:
        text = ''

        if 'user_id' not in session:
            return redirect('/error')

        if request.method == 'GET':
            return render_template('add_question.html', title='Добавить вопрос')
        if request.method == 'POST':
            points = int(request.form.get('point'))
            if 0 < points < 10000 and request.form.get('text') and request.form.get('title'):
                user_model = db.session.query(Memeuser).filter_by(id=session['user_id']).first()
                if int(user_model.point) < points:
                    text += 'Недостаточно pointов'
                    return render_template('add_question.html', title='Добавить вопрос', text=text)

                category = db.session.query(Memecategory).filter_by(
                    category=request.form.get('category')).first().id

                question = add_question_func(request.form.get('title'), request.form.get('text'), points, category,
                                             user_model)
            else:
                text += 'Проверьте правильность введённых данных'
                return render_template('add_question.html', title='Добавить вопрос', text=text)
            return redirect('/question/{}'.format(question.id))
    except Exception:
        return redirect('/error')


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
    if not is_admin(session):
        return redirect('/error')
    users = db.session.query(Memeuser).all()
    return render_template('admin.html', title='Админ', users=users)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    try:
        if 'user_id' not in session:
            return redirect('/error')
        user_model = user_check(session['user_id'], db, Memeuser)
        questions = db.session.query(Memequestion).filter_by(id_user=user_model.id).all()
        answers = db.session.query(Memeanswer).filter_by(id_user=user_model.id).all()

        if request.method == 'GET':
            return render_template('profile.html', title='Профиль', user_model=user_model, questions=questions,
                                   category=db.session.query(Memecategory), answers=answers)
        elif request.method == 'POST':
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
                    return render_template('profile.html', title='Профиль',
                                           user_model=user_model, category=db.session.query(Memecategory))
                user_model.photo = filename

                db.session.commit()
                with open(r"C:\Users\ilyam\PycharmProjects\MemeSite\static\{}\{}".format(user_model.id, '/image_.' +
                                                                                                        request.files.get(
                                                                                                            'file').mimetype.split(
                                                                                                            '/')[1]),
                          'wb') as photo:
                    photo.write(request.files.get('file').read())
                return redirect('/profile')

            return render_template('profile.html', title='Профиль',
                                   user_model=user_model, category=db.session.query(Memecategory))
    except Exception:
        return redirect('/error')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(port=8070, host='127.0.0.1')
