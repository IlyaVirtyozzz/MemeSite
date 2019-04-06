from constant import *
from database import *
from flask import url_for
from functions import *
import shutil, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class MemeWiki(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=False, nullable=False)
    name_article = db.Column(db.String(32), unique=False, nullable=False)
    content = db.Column(db.String(5000), unique=False, nullable=False)
    photo = db.Column(db.String(100), unique=False, nullable=True)

    def __repr__(self):
        return "<MemeWiki {} {} {} {} {} >".format(self.id, self.name, self.name_article, self.content, self.photo)


def add_new_wiki(name, name_article, content, photo='/static/MemePediaImageStandart.jpg'):
    wiki = MemeWiki(
        name=name,
        name_article=name_article,
        content=content,
        photo=photo)

    db.session.add(wiki)
    db.session.commit()

db.create_all()
add_new_wiki('Енотик', 'Глад валакас', '''Глад Валакас известен не только своим образом, но и множеством фирменных фраз , я пажилой антоним, я люблю тупа бибу солсать''')

