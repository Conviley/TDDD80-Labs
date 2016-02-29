import json
import requests
from flask import *
from lab2 import User,Messages

url = 'http://127.0.0.1:9089/'
urlsharp = 'http://flask-tjegu689tddd80.openshift.ida.liu.se/'

def add_user(username,password):
    adduser = requests.post(urlsharp + 'user', json=dict(username = username,password = password))
def add_message(msg,user_id,token):
    headers = {'authorization' : token}
    addmsg = requests.post(urlsharp + "messages",data = json.dumps(dict(message = msg, user_id = user_id)), headers=headers)#json.dumps(dict(message=msg)))

def mark_read(id,UserID,token):
    headers = {'authorization' : token}
    markmsg = requests.post(urlsharp + 'messages/'+str(id)+'/flag/' + str(UserID), headers=headers)

def get_message(msgid):
    get_msg = requests.get('http://flask-tjegu689tddd80.openshift.ida.liu.se/messages'+str(msgid))

def print_msgs():
    print(Messages.query.all())

def print_users():
    print(User.query.all())

def del_message(id, token):
    headers = {'authorization' : token}
    delmsg = requests.delete(urlsharp + 'messages/' + str(id), headers=headers)

def del_user(id,token,user_id):
    headers = {'authorization' : token, 'user' : user_id}
    delmsg = requests.delete('http://flask-tjegu689tddd80.openshift.ida.liu.se/users/' + str(id), headers = headers)

def login(username,password):
    token =  requests.post(urlsharp + "user/login", json=(dict(username = username,password = password)))
    print(token)

def logout(token):
    headers = {'authorization' : token}
    requests.post(urlsharp + "user/logout",headers = headers)#json={'token':token})
