from database import *
from flask import url_for
from constant import PATH
import shutil, os


# Зарегестрирован ли пользователь?
def user_check(id_user, db, Memeuser):
    return db.session.query(Memeuser).filter_by(id=id_user).first()


# Админ ли пользователь?
def is_admin(session):
    if 'user_id' in session:
        return db.session.query(Admins).filter_by(id_user=session['user_id']).first()


# Вопрос пользователя?
def is_user_question(id_question, id_user):
    question = db.session.query(Memequestion).filter_by(id=id_question).first()
    if question:
        return question.id_user == id_user
    return None


# Ответ пользователя?
def is_user_answer(id_question, id_answer, id_user):
    answer = db.session.query(Memeanswer).filter_by(id=id_answer, id_question=id_question).first()
    if answer:
        return answer.id_user == id_user
    return None


# Закрыть вопрос
def close_question_func(id_question):
    question = db.session.query(Memequestion).filter_by(id=id_question).first()
    question.active = False
    db.session.commit()


# Выбор правильного ответа
def true_answer_func(id_question, id_answer, session):
    answer = db.session.query(Memeanswer).filter_by(id_question=id_question, id=id_answer).first()
    question = db.session.query(Memequestion).filter_by(id=id_question).first()
    user = db.session.query(Memeuser).filter_by(id=answer.id_user).first()
    if session['user_id'] == user.id:
        return
    if question.active:
        user.point += question.point
        answer.point += question.point
        question.point = 0
        answer.true = True
        question.active = False
        db.session.commit()


# Создание нового пользователя
def add_new_user(email, user_name, sex, password):
    user = Memeuser(email=email,
                    name=user_name,
                    sex=sex,
                    password=password,
                    point=100,
                    photo=url_for('static', filename='image.jpg'))

    db.session.add(user)
    db.session.commit()

    newpath = PATH + '/static/{}/'.format(user.id)
    if not os.path.exists(newpath):
        os.mkdir(newpath)

    shutil.copy(r'static/image.jpg', r'static/{}/'.format(user.id))
    user.photo = 'static/{}/image.jpg'.format(user.id)
    db.session.commit()

    return user


# Фильтрация вопросов
def filter_questions(id_category, active):
    if id_category == 1:
        questions = db.session.query(Memequestion).all()
    else:
        questions = db.session.query(Memequestion).filter_by(id_category=id_category).all()
    if active == 1:
        return questions
    else:
        return sorted(questions, key=lambda x: x.active, reverse=True)


# Добавление вопроса
def add_question_func(title, text, points, id_category, user_model):
    question = Memequestion(id_user=user_model.id,
                            title=title,
                            text=text,
                            point=points,
                            active=True,
                            id_category=id_category)

    user_model.point -= points
    db.session.add(question)
    db.session.commit()
    return question


# Вход пользователя
def login_func(email, password, session):
    user_model = db.session.query(Memeuser).filter_by(email=email).first()
    if user_model and user_model.password == password:
        session.clear()
        session['username'] = user_model.name
        session['user_id'] = user_model.id
        return True
    else:
        return False


# Добавление ответа
def add_answer_func(session, id_question, text, point):
    answer = Memeanswer(id_user=session['user_id'], id_question=id_question, text=text, true=False, point=point)
    db.session.add(answer)
    db.session.commit()


# Удаление пользователя
def delete_user_func(id_user):
    if id_user:
        question = db.session.query(Memequestion).filter_by(id_user=id_user).first()
        answers = db.session.query(Memeanswer).filter_by(id_user=id_user).all()
        user = db.session.query(Memeuser).filter_by(id=id_user).first()

        if answers:
            for answer in answers:
                db.session.delete(answer)
                db.session.commit()

        if question:
            db.session.delete(question)
            db.session.commit()

        if user:
            shutil.rmtree('static/{}'.format(user.id))
            db.session.delete(user)
            db.session.commit()

            return True

    return None


# Удаление вопроса
def delete_question_func(id_question):
    if id_question:
        question = db.session.query(Memequestion).filter_by(id=id_question).first()
        answers = db.session.query(Memeanswer).filter_by(id_question=id_question).all()
        if answers:
            for answer in answers:
                db.session.delete(answer)
                db.session.commit()

        if question:
            db.session.delete(question)
            db.session.commit()
            return True
    return


# Удаление ответа
def delete_answer_func(id_question, id_answer):
    if id_question and id_answer:
        answer = db.session.query(Memeanswer).filter_by(id=id_answer, id_question=id_question).first()
        if answer:
            db.session.delete(answer)
            db.session.commit()
            return True
    return
