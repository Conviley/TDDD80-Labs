import json
from flask import Flask,request,jsonify,abort


app = Flask(__name__)

msgs = []
global id_counter
id_counter = 1

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/messages', methods=['GET'])
def all_msgs():
    return json.dumps(msgs)


@app.route('/messages', methods=['POST'])
def add_msg():
    global id_counter
    msg = request.get_json(force=True)
    if(len(msg["message"])>140):
        abort(404)
    msg['id'] = id_counter
    msg['readBy'] = []
    msgs.append(msg)
    id_counter += 1
    return "OK"


@app.route('/messages/<MessageID>', methods=['GET'])
def get_msg(MessageID):
    for i in msgs:
        if i['id'] == int(MessageID):
            return jsonify(i)


@app.route('/messages/<MessageID>', methods=['DELETE'])
def remove_msg(MessageID):
    if not MessageID and not msgs:
        abort(400)
    elif not msgs:
        abort(400)
    for msg in msgs:
        if msg['id'] == int(MessageID):
            msgs.remove(msg)
    return "OK"


@app.route('/messages/<MessageID>/flag/<UserId>', methods = ['POST'])
def mark_read(MessageID,UserId):
    if not MessageID and not UserId:
        abort(400)
    for msg in msgs:
        if msg['id'] == int(MessageID):
            msg["readBy"].append(UserId)
    return "OK"


@app.route('/messages/unread/<UserId>', methods=['GET'])
def unread_msg(UserId):
    if not UserId:
        abort(400)
    unreadmsgs = []
    for i in msgs:
        if UserId not in i['readBy']:
            unreadmsgs.append(i)
    return json.dumps(unreadmsgs)


if __name__ == '__main__':
    app.debug = True
    app.run(port=9089)