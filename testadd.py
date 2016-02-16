import json
import requests
from flask import *
from lab2database import User,Messages

url = 'http://127.0.0.1:9089/'
urlsharp = 'http://flask-tjegu689tddd80.openshift.ida.liu.se/'

def add_user(User):
    adduser = requests.post(urlsharp + 'add_user', json=User)
def add_message(msg):
    addmsg = requests.post('http://flask-tjegu689tddd80.openshift.ida.liu.se/messages',data = json.dumps(msg))#json.dumps(dict(message=msg)))

def mark_read(id,UserID):
    markmsg = requests.post('http://flask-tjegu689tddd80.openshift.ida.liu.se/messages/'+str(id)+'/flag/' + str(UserID))

def get_message(msgid):
    get_msg = requests.get('http://flask-tjegu689tddd80.openshift.ida.liu.se/messages'+str(msgid))

def print_msgs():
    print(Messages.query.all())

def print_users():
    print(User.query.all())

def del_message(id):
    delmsg = requests.delete('http://flask-tjegu689tddd80.openshift.ida.liu.se/messages/' + str(id))
    # remove = Messages.query.filter_by(id=id).delete()
    # db.session.commit()
    # Messages.query.delete()
