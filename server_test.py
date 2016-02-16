import os
from flask import json
import lab2
import unittest
import tempfile
from lab2database import Messages, User

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        lab2.app.config['TESTING'] = True
        self.app = lab2.app.test_client()
        lab2.db_reset()


    def tearDown(self):
        pass


    def test_root_db(self):
        rv = self.app.get('/')
        self.assertEqual(b'Hello000 World!',rv.data)


    def test_get_all_msgs(self):
        messages_sent = 10
        for i in range(messages_sent):
            self.send_message("Message")

        rv = self.get_all_msgs()
        actual_msgs_sent= json.loads(rv.data)
        self.assertEqual(len(actual_msgs_sent),messages_sent)

        for msg in actual_msgs_sent:
            self.assertEqual(msg["message"],"Message")

    def test_get_all_users(self):
        self.add_user("Conviley")
        self.add_user("Rubbehill")
        rv = self.get_all_users()
        users = json.loads(rv.data)
        self.assertEqual(len(users), 2)


    def test_get_message(self):
        self.send_message("hello")
        rv = self.get_message(1)
        actual_message = json.loads(rv.data)
        self.assertEqual(actual_message['message'],"hello")
        rv = self.get_message(2)
        self.assertEqual(rv.status_code,400)


    def test_remove_message(self):
        self.send_message("hello")
        self.send_message("hi")
        self.add_user("Conviley")
        self.mark_read(1,1)
        rv = self.get_all_msgs()
        all_msgs = json.loads(rv.data)
        self.delete_message(1)
        r = self.get_all_msgs()
        msgs_left = json.loads(r.data)
        self.assertEqual(len(all_msgs)-1, len(msgs_left))

    def test_mark_read(self):
        self.send_message("Hello Conviley")
        self.add_user("Conviley")
        self.mark_read(1,1)
        rv = self.get_all_msgs()
        marked_msg = json.loads(rv.data)
        reader_list = marked_msg[0]['readBy'][0]
        assert "Conviley" in reader_list

    def test_unread(self):
        self.send_message("Helloes")
        self.send_message("hi")
        self.add_user("Conviley")
        self.add_user("Ribbedy")
        self.mark_read(1,1)

        rv = self.app.get('/messages/unread/' + str(2))
        unread_msg = json.loads(rv.data)
        assert ["Ribbedy",2] not in unread_msg[0]['readBy']

    def test_add_user(self):
        rv = self.add_user("Conviley")
        is_user = True
        if not User.query.filter_by(id = 1):
            is_user = False
        self.assertEqual(is_user,True)

    def test_add_message(self):
        self.send_message("Hello")
        rv = self.app.get('/messages/' + str(1))
        added_message= json.loads(rv.data)
        self.assertEqual(added_message['id'],1)


    def get_all_msgs(self):
        return self.app.get('/messages')

    def get_all_users(self):
        return self.app.get('/users')

    def send_message(self, message):
        return self.app.post('/messages', data = json.dumps(message),content_type="application/json" )

    def add_user(self, user):
        return self.app.post('/add_user', data = json.dumps(user),content_type="application/json" )


    def get_message(self, MessageID):
        return self.app.get('/messages/' + str(MessageID))

    def delete_message(self,MessageID):
        return self.app.delete('/messages/' + str(MessageID))

    def mark_read(self,MessageID,UserID):
        return self.app.post('http://127.0.0.1:9089/messages/'+str(MessageID)+'/flag/' + str(UserID))

    def add_user(self,User):
        return self.app.post('http://127.0.0.1:9089/add_user', data=json.dumps(User), content_type ="application/json")



if __name__ == '__main__':
    unittest.main()