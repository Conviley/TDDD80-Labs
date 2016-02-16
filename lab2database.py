#from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from lab2 import db
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/pp.db'
#db = SQLAlchemy(app)

user_messages = db.Table('user_messages', db.Model.metadata,
    db.Column('messages_id', db.Integer, db.ForeignKey('messages.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

    messages_read = db.relationship('Messages', secondary=user_messages, back_populates = "readBy")
    # tags = db.relationship('Messages', secondary=read_messages,
    #     backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username):
        self.username = username

    def get_name(self):
        return self.username

    def get_id(self):
        return self.id

    def get_dict(self):
        return  {'id' : self.get_id(),'username': self.get_name()}

    def __repr__(self):
        return '<User %r>' % self.username + '<Id: %r>' % self.id

class Messages(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    message = db.Column(db.String(140))

    readBy = db.relationship('User', secondary=user_messages, back_populates = "messages_read")


    def __init__(self,message):
         self.message = message

    def get_msg(self):
        return self.message

    def get_id(self):
        return self.id

    def get_dict(self):
        read_list=[]
        for i in self.readBy:
            read_list.append([i.get_name(),i.get_id()])
        return  {'id' : self.get_id(), 'message' : self.get_msg(),'readBy' : read_list}

    def __repr__(self):
        return '<Message %r>' % self.message + '<Id: %r>' % self.id