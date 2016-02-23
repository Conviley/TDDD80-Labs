from flask import json
import lab2
import unittest
from lab2 import User, Messages


class ServerTestCase(unittest.TestCase):

    def setUp(self):
        lab2.app.config['TESTING'] = True
        self.app = lab2.app.test_client()
        lab2.db_reset()

    def tearDown(self):
        pass

    def test_root_db(self):
        rv = self.app.get('/')
        self.assertEqual(b'Hello000 World!', rv.data)

    def test_get_all_msgs(self):
        messages_sent = 10
        self.add_user("Conviley", "password")
        self.login("Conviley", "password")
        user = User.query.filter_by(username="Conviley").first()
        token = user.token.all()[0].token
        for i in range(messages_sent):
            self.send_message("Message",1, token)
        rv = self.get_all_messages()
        actual_msgs_sent = json.loads(rv.data)
        self.assertEqual(len(actual_msgs_sent), messages_sent)
        for msg in actual_msgs_sent:
            self.assertEqual(msg["message"], "Message")

    def test_get_all_users(self):
        self.add_user("Conviley", "password")
        self.add_user("Rubbehill", "password")
        rv = self.get_all_users()
        users = json.loads(rv.data)
        self.assertEqual(len(users), 2)

    def test_get_message(self):
        self.add_user("Conviley", "password")
        self.login("Conviley", "password")
        user = User.query.filter_by(username = "Conviley").first()
        token = user.token.all()[0].token
        self.send_message("hello",1, token)
        rv = self.get_message(1)
        actual_message = json.loads(rv.data)
        self.assertEqual(actual_message['message'], "hello")
        rv = self.get_message(2)
        self.assertEqual(rv.status_code,400)

    def test_remove_message(self):
        self.add_user("Conviley", "password")
        self.login("Conviley", "password")
        self.add_user("rubbe", "password")
        self.login("rubbe", "password")
        user = User.query.filter_by(username = "Conviley").first()
        token = user.token.all()[0].token
        user2 = User.query.filter_by(username = "rubbe").first()
        token2 = user2.token.all()[0].token
        self.send_message("hello",1,token)
        self.send_message("hi",2,token2)
        self.mark_read(1,1,token)
        rv = self.get_all_messages()
        all_msgs = json.loads(rv.data)
        print(all_msgs,"asd")
        self.delete_message(1,token)
        r = self.get_all_messages()
        msgs_left = json.loads(r.data)
        self.assertEqual(len(all_msgs)-1, len(msgs_left))

    def test_remove_user(self):
        self.add_user("Conviley","password")
        rv = self.get_all_users()
        all_users = json.loads(rv.data)
        self.delete_user(1)
        r = self.get_all_users()
        users_left = json.loads(r.data)
        self.assertEqual(len(all_users)-1, len(users_left))

    def test_mark_read(self):
        self.add_user("Conviley", "password")
        self.login("Conviley", "password")
        user = User.query.filter_by(username = "Conviley").first()
        token = user.token.all()[0].token
        self.send_message("Hello Conviley",1, token)
        self.mark_read(1,1,token)
        rv = self.get_all_messages()
        marked_msg = json.loads(rv.data)
        reader_list = marked_msg[0]['readBy'][0]
        assert "Conviley" in reader_list

    def test_unread(self):
        self.add_user("Conviley","password")
        self.add_user("Ribbedy", "qwerty")
        self.login("Conviley", "password")
        self.login("Ribbedy", "qwerty")
        user1 = User.query.filter_by(username = "Conviley").first()
        user2 = User.query.filter_by(username = "Ribbedy").first()
        token1 = user1.token.all()[0].token
        token2 = user2.token.all()[0].token
        self.send_message("Helloes",1,token1)
        self.send_message("hi",2,token2)
        self.mark_read(1,1,token1)
        #print(self.mark_read(1,1,token1))
        rv = self.app.get('/messages/unread/' + str(2))
        unread_msg = json.loads(rv.data)
        assert ["Ribbedy",2] not in unread_msg[0]['readBy']

    def test_add_user(self):
        rv = self.add_user("Conviley","password")
        is_user = True
        if not User.query.filter_by(id = 1):
            is_user = False
        self.assertEqual(is_user,True)

    def test_add_message(self):
        self.add_user("Conviley", "password")
        self.login("Conviley", "password")
        user = User.query.filter_by(username = "Conviley").first()
        print(user.token.all()[0].token,"is token")
        token = user.token.all()[0].token
        self.send_message("Hello",1,token)
        rv = self.app.get('/messages/' + str(1))
        added_message= json.loads(rv.data)
        self.assertEqual(added_message['id'],1)

    def test_logout(self):
        self.add_user("Conviley", "password")
        self.login("Conviley", "password")
        user = User.query.filter_by(username = "Conviley").first()
        token = user.token.all()[0].token
        self.logout(token)
        userafter = User.query.filter_by(username = "Conviley").first()
        self.assertEqual(userafter.token.all()[0].token,None)


    def send_message(self, message, user_id, token):
        headers = {'authorization': token}
        return self.app.post('/messages', data = json.dumps(dict(message=message, user_id=user_id)), headers=headers, content_type="application/json")

    def add_user(self, username, password):
        return self.app.post('/user', data = json.dumps(dict(username=username, password=password)), content_type="application/json")

    def login(self, username, password):
        return self.app.post('/user/login', data=json.dumps(dict(username=username, password=password)), content_type="application/json")

    def get_all_messages(self):
        return self.app.get('/messages')

    def get_all_users(self):
        return self.app.get('/users')

    def get_message(self, message_id):
        return self.app.get('/messages/' + str(message_id))

    def mark_read(self,user_id, message_id,token):
        headers = {'authorization': token}
        return self.app.post('/messages/'+str(message_id)+'/flag/' + str(user_id),headers = headers,content_type="application/json")

    def delete_message(self,message_id,token):
        headers = {'authorization': token}
        return self.app.delete('/messages/' + str(message_id),headers=headers)

    def delete_user(self, user_id):
        return self.app.delete('/users/' + str(user_id))

    def logout(self,token):
        headers = {'authorization':token}
        return self.app.post('/user/logout', headers=headers)


if __name__ == '__main__':
    unittest.main()