import json
import requests
from flask import *

def send_message(msg):
    message = json.dumps({"message" : msg})
    addmsg = requests.post('http://127.0.0.1:9089/messages', data=message)

def del_message(id):
    delmsg = requests.delete('http://127.0.0.1:9089/messages/' + str(id))

def mark_read(id,UserID):
    markmsg = requests.post('http://127.0.0.1:9089/messages/'+str(id)+'/flag/' + UserID)