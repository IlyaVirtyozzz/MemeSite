from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqldatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = SQLAlchemy(app)
IMAGE_RESOLUTION = {'jpeg', 'jpg', 'png'}
file_name_ = inspect.getframeinfo(inspect.currentframe()).filename
PATH = os.path.dirname(os.path.abspath(file_name_))