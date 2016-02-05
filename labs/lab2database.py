from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from unohelper import Base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/pp.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

    def __init__(self, username):
        self.username = username
        self.id = id(self)

    def __repr__(self):
        return '<User %r>' % self.username

class Messages(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    message = db.Column(db.String(140))

    def __init__(self,message):
        self.message = message
        self.id = id(self)

    def get_msg(self):
        return self.message

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<Message %r>' % self.message + '<Id: %r>' % self.id