import json
import os
from flask import Flask,request, jsonify,abort, Response, g, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
msgs = []

if "OPENSHIFT_POSTGRESQL_DB_URL" in os.environ:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/pp.db"

app.config['SECRET_KEY'] = 'gurra bor i en liten vagn av bambu'
db = SQLAlchemy(app)


user_messages = db.Table('user_messages', db.Model.metadata,
    db.Column('messages_id', db.Integer, db.ForeignKey('messages.id',ondelete="cascade")),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete="cascade"))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))

    token = db.relationship('Token',backref='user',lazy = 'dynamic')
    written_messages = db.relationship('Messages', backref='user',lazy='dynamic')
    messages_read = db.relationship('Messages', secondary=user_messages, back_populates = "readBy")


    # tags = db.relationship('Messages', secondary=read_messages,
    #     backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username,password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password,password)

    def generate_auth_token(self,experation=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=experation)
        token = s.dumps({'id':self.id})
        token = Token(token.decode('ascii'),self.id)
        db.session.add(token)
        db.session.commit()
        return s.dumps({'id':self.id})

    def get_name(self):
        return self.username

    def get_password(self):
        return self.password

    def get_id(self):
        return self.id

    def get_token(self):
        return self.token

    def get_written_messages(self):
        print(self.written_messages,"written messages")
        return self.written_messages

    def get_dict(self):
        return  {'id' : self.get_id(),'username': self.get_name()}

    def __repr__(self):
        return '<User %r>' % self.username + '<Id: %r>' % self.id + '<Password %r>' % self.password + '<Token %r>' % self.token

class Messages(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    message = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    readBy = db.relationship('User', secondary=user_messages, back_populates = "messages_read",cascade='all,delete-orphan',single_parent=True)

    def __init__(self,message, user_id):
        self.message = message
        self.user_id = user_id

    def get_msg(self):
        return self.message

    def get_id(self):
        return self.id

    def get_dict(self):
        read_list=[]
        for i in self.readBy:
            read_list.append([i.get_name(),i.get_id()])
        return  {'id' : self.get_id(), 'message' : self.get_msg(),'readBy' : read_list, 'written_by' : self.user_id}

    def __repr__(self):
        return '<Message %r>' % self.message + '<Id: %r>' % self.id

class Token(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    token = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self,token, user_id):
        self.token = token
        self.user_id = user_id

    def __repr__(self):
        return '<token %r>' % self.token + '<Id: %r>' % self.id

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        print(s.loads(token))
        data = s.loads(token)

    except SignatureExpired:
        print("expired")
        return None
    except BadSignature:
        print("bad")
        return None
    user = User.query.get(data['id'])
    print(user.token.all()[0], "2ad")
    tokens = user.token.all()
    print(tokens,'token')
    for tok in tokens:
        print(tok.token, 'tok')
        if token == tok.token:
            return user
    if user.token == token:
        return user
    else:
        print("you need to be logged in 1!")
        abort(401)


def verify_login(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        token = request.headers.get('authorization')
        if token == None:
            abort(401)
        if token is None:
            print("You need to be logged in 2!")
        g.user = verify_auth_token(token)
        if g.user is None:
            print("asdasd")
            abort(401)
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
def hello_world():
    return 'Hello000 World!'


@app.route('/user/login', methods=['POST'])
def login():
    user_info = request.get_json()
    try_users = User.query.filter_by(username=user_info['username']).first()
    if try_users is None:
        return "User or password is not matching"
    if try_users.check_password(user_info['password']):
        return try_users.generate_auth_token()
    else:
        return "User or password is not matching"


@app.route('/user/logout', methods=['POST'])
@verify_login
def logout():
    token = request.headers.get('authorization')
    print(token, "header")
    user = verify_auth_token(token)
    print(user)
    print(user.token.all(), "logouts")
    tokens = user.token.all()
    for tok in tokens:
        if tok.token == token:
            Token.query.filter_by(token = token).delete()
    db.session.commit()
    return ""


@app.route('/messages', methods=['GET'])
def all_msgs():
    message_list = []
    messages = Messages.query.all()
    for i in messages:
        message_list.append(i.get_dict())
    ret = json.dumps(message_list, indent=4, sort_keys=True,)
    resp = Response(response=ret, status=200, mimetype="application/json")
    return resp


@app.route('/users', methods=['GET'])
def all_users():
    user_list = []
    users = User.query.all()
    print(users)
    for i in users:
       user_list.append(i.get_dict())
    ret = json.dumps(user_list, indent=4, sort_keys=True,)
    resp = Response(response=ret, status=200, mimetype="application/json")
    return resp


def get_all_messages(seq):
    message_list = []
    messages = Messages.query.all()
    for i in messages:
        seq.append(i.get_dict())


@app.route('/messages/<MessageID>', methods=['GET'])
def get_msg(MessageID):
    message_list = []
    get_all_messages(message_list)
    for i in message_list:
        if i['id'] == int(MessageID):
            return jsonify(i)
    abort(400)


@app.route('/messages/<MessageID>', methods=['DELETE'])
@verify_login
def remove_msg(MessageID):
    token = request.headers.get('authorization')
    user = g.user
    msg_to_remove = Messages.query.filter_by(id=int(MessageID)).first()
    if not msg_to_remove or msg_to_remove.user_id != user.id:
        abort(400)
    Messages.query.filter_by(id=MessageID).delete()
    db.session.commit()
    return ""


@app.route('/messages/<MessageID>/flag/<UserId>', methods=['POST'])
@verify_login
def mark_read(MessageID, UserId):
    Messages.query.all()
    message = Messages.query.filter_by(id=int(MessageID)).first()
    user = User.query.filter_by(id=int(UserId)).first()
    if not user:
        abort(400)
    message.readBy.append(user)
    db.session.commit()
    return ""


@app.route('/messages/unread/<UserId>', methods=['GET'])
@verify_login
def unread_msg(UserId):
    message_list = []
    if not User.query.filter_by(id=UserId).first():
        abort(400)
    unreadmsgs = Messages.query.filter(~Messages.readBy.any(id=UserId))
    for i in unreadmsgs:
        message_list.append(i.get_dict())
    ret = json.dumps(message_list, indent=4, sort_keys=True,)
    resp = Response(response=ret, status=200, mimetype="application/json")
    return resp


@app.route('/user', methods=['POST'])
def add_user():
    user = request.get_json()
    if not User.query.filter_by(username=user['username']).first():
        user = User(user['username'], user['password'])
        db.session.add(user)
        db.session.commit()
    else:
        abort(400)
    return ""


@app.route('/users/<UserID>', methods=['DELETE'])
def remove_user(UserID):
    if not User.query.filter_by(id=int(UserID)).first():
        abort(400)
    User.query.filter_by(id=UserID).delete()
    db.session.commit()
    return ""


@app.route('/messages', methods=['POST'])
@verify_login
def add_msg():
    msg = request.get_json(force=True)
    #token = request.headers.get('authorization')
    user = User.query.filter_by(id = msg['user_id']).first()
    if not msg:
        abort(400)
    msg = Messages(msg['message'],user.id)
    db.session.add(msg)
    db.session.commit()
    return ""


def db_reset():
    db.drop_all()
    db.create_all()

db.create_all()
if __name__ == '__main__':
    app.debug = True
    db_reset()
    app.run(port=9089)

app.debug = True
