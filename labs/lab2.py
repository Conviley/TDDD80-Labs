import code
import json


from flask import Flask,request,jsonify,abort, current_app, make_response
from lab2database import User,Messages,db
app = Flask(__name__)
msgs = []
global id_counter, message_list
message_list = []


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/messages', methods=['GET'])
def all_msgs():
    global message_list
    messages = Messages.query.all()
    print(messages, "messages")
    for i in range(len(messages)):
        if {'id' : messages[i].get_id(), 'message' : messages[i].get_msg()} not in message_list:
            message_list.append({'id' : messages[i].get_id(), 'message' : messages[i].get_msg()})
    print(json.dumps(message_list, indent= 2, sort_keys=True))
    #json.dumps(message_list, indent= 2, sort_keys=True)
    return json.dumps(message_list, sort_keys=True)#jsonify(Messages = message_list)


@app.route('/messages/<MessageID>', methods=['GET'])
def get_msg(MessageID):
    for i in message_list:
        if i['id'] == MessageID:
            return jsonify(i)
    abort(400)


@app.route('/messages/<MessageID>', methods=['DELETE'])
def remove_msg(MessageID):
    global message_list
    remove = Messages.query.filter_by(id=MessageID).delete()
    update = Messages.query.all()
    #db.update(Messages)
    print(update)
    message_list = []
    db.session.commit()
    return ""


@app.route('/messages/<MessageID>/flag/<UserId>', methods = ['POST'])
def mark_read(MessageID,UserId):
    has_marked = False
    for msg in msgs:
        if msg['id'] == int(MessageID):
            msg["readBy"].append(UserId)
            has_marked = True
    if not has_marked:
        abort(400)
    return ""


@app.route('/messages/unread/<UserId>', methods=['GET'])
def unread_msg(UserId):
    if not isinstance(str,UserId):
        abort(400)
    unreadmsgs = []
    for i in msgs:
        if UserId not in i['readBy']:
            unreadmsgs.append(i)
    return json.dumps(unreadmsgs)


@app.route('/add_user',methods=['POST'])
def add_user():
    user = request.get_json()
    user = User(user)
    db.session.add(user)
    db.session.commit()
    return ""


@app.route('/messages/add', methods=['POST'])
def add_msg():
    global id_counter
    msg = request.get_json()
    msg = Messages(msg)
    db.session.add(msg)
    db.session.commit()
    return ""


if __name__ == '__main__':
    app.debug = True
    app.run(port=9089)
