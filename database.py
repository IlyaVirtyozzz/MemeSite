from constant import *


class Memeuser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    sex = db.Column(db.String(10), unique=False, nullable=False)
    point = db.Column(db.Integer, unique=False, nullable=False)
    photo = db.Column(db.String(100), unique=False, nullable=False)

    def __repr__(self):
        return "<Memeuser {} {} {} {} {} {}>".format(self.id, self.name, self.email, self.password, self.sex,
                                                     self.point)


class Memeanswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, unique=False, nullable=False)
    id_question = db.Column(db.Integer, unique=False, nullable=False)
    text = db.Column(db.String(2000), unique=False, nullable=False)
    point = db.Column(db.Integer, unique=False, nullable=False)
    true = db.Column(db.Boolean)

    def __repr__(self):
        return "<Memeuser {} {} {} {} {}>".format(self.id, self.id_user, self.text, self.true, self.point)


class Memecategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return "<Memeuser {} {}>".format(self.id, self.category)


class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<Admins {} {}>".format(self.id, self.id_user)


class Memequestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, unique=False, nullable=False)
    title = db.Column(db.String(80), unique=False, nullable=False)
    text = db.Column(db.String(2000), unique=False, nullable=False)
    id_category = db.Column(db.String(10), unique=False, nullable=False)
    point = db.Column(db.Integer, unique=False, nullable=False)
    active = db.Column(db.Boolean)

    def __repr__(self):
        return "<Memeuser {} {} {} {} {} {} {}>".format(self.id, self.id_user, self.title, self.text, self.id_category,

                                                        self.point, self.active)


def add_category():
    for i in ['Все подряд', 'Политика', 'Животные', 'Игры', 'Русские', '18+', 'Аниме', 'Ностальгия',
              'Техно-научные', 'АнтиK-pop', 'Другие']:
        category = Memecategory(category=i)
        db.session.add(category)
        db.session.commit()


def add_admin(id_user):
    admin = Admins(id_user=id_user)
    db.session.add(admin)
    db.session.commit()


if __name__ == '__main__':
    db.create_all()
    add_admin(1)