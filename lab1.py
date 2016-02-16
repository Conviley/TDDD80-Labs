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
    if(len(msg["message"])>140 and not isinstance(str,msg["message"])):
        abort(400)
    msg['id'] = str(id_counter)
    msg['readBy'] = []
    msgs.append(msg)
    id_counter += 1
    return ""


@app.route('/messages/<MessageID>', methods=['GET'])
def get_msg(MessageID):
    for i in msgs:
        if i['id'] == MessageID:
            return jsonify(i)
    abort(400)

@app.route('/messages/<MessageID>', methods=['DELETE'])
def remove_msg(MessageID):
    has_removed = False
    if not msgs:
        abort(400)
    for msg in msgs:
        if msg['id'] == MessageID:
            msgs.remove(msg)
            has_removed = True
    if not has_removed:
        abort(400)
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


if __name__ == '__main__':
    app.debug = True
    app.run(port=9089)