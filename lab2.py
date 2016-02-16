import code
import json


from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask,request,jsonify,abort, current_app, make_response, Response
from lab2database import User,Messages,db
app = Flask(__name__)
msgs = []

if "OPENSHIFT_POSTGRESQL_DB_URL" in os.environ:
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
else:
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:////tmp/test.db"

#db = SQLAlchemy(app)



@app.route('/')
def hello_world():
    return 'Hello000 World!'


@app.route('/messages', methods=['GET'])
def all_msgs():
    message_list = []
    messages = Messages.query.all()
    for i in messages:
        message_list.append(i.get_dict())
    ret = json.dumps(message_list,indent=4,sort_keys=True,)
    resp = Response(response=ret,status=200,mimetype="application/json")
    return resp

@app.route('/users', methods=['GET'])
def all_users():
    user_list = []
    users = User.query.all()
    for i in users:
       user_list.append(i.get_dict())
    ret = json.dumps(user_list,indent=4,sort_keys=True,)
    resp = Response(response=ret,status=200,mimetype="application/json")
    return resp

def get_all_messages(seq):
    message_list = []
    messages = Messages.query.all()
    for i in messages:
        seq.append(i.get_dict())


@app.route('/messages/<MessageID>', methods=['GET'])
def get_msg(MessageID):
    message_list=[]
    get_all_messages(message_list)
    for i in message_list:
        if i['id'] == int(MessageID):
            return jsonify(i)
    abort(400)


@app.route('/messages/<MessageID>', methods=['DELETE'])
def remove_msg(MessageID):
    if not Messages.query.filter_by(id=int(MessageID)).first():
        abort(400)
    Messages.query.filter_by(id=MessageID).delete()
    db.session.commit()
    return ""


@app.route('/messages/<MessageID>/flag/<UserId>', methods = ['POST'])
def mark_read(MessageID,UserId):
    messages = Messages.query.all()
    message = Messages.query.filter_by(id=int(MessageID)).first()
    user = User.query.filter_by(id=int(UserId)).first()
    print(user)
    if not user:
        abort(400)
    message.readBy.append(user)
    db.session.commit()
    return ""


@app.route('/messages/unread/<UserId>', methods=['GET'])
def unread_msg(UserId):
    message_list = []
    if not User.query.filter_by(id = UserId).first():
        abort(400)
    unreadmsgs = Messages.query.filter(~Messages.readBy.any(id = UserId))
    for i in unreadmsgs:
        message_list.append(i.get_dict())
    ret = json.dumps(message_list,indent=4,sort_keys=True,)
    resp = Response(response=ret,status=200,mimetype="application/json")
    return resp


@app.route('/add_user',methods=['POST'])
def add_user():
    user = request.get_json()
    if not User.query.filter_by(username=user).first():
        print("one up")
        user = User(user)
        db.session.add(user)
        db.session.commit()
    else:
        abort(400)
    return ""


@app.route('/messages', methods=['POST'])
def add_msg():
    global id_counter
    msg = request.get_json(force=True)
    if not msg:
        abort(400)
    msg = Messages(msg)
    db.session.add(msg)
    db.session.commit()
    return ""

def db_reset():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    db_reset()
    app.run(port=9089)

app.debug = True