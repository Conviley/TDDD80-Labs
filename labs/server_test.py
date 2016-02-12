import os
from flask import json
import lab2
import unittest
import tempfile

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        lab2.app.config['TESTING'] = True
        self.app = lab2.app.test_client()
        lab2.db_reset()

    def tearDown(self):
        pass

    def test_root_db(self):
        rv = self.app.get('/')
        self.assertEqual(b'Hello World!',rv.data)

    def test_get_all_msgs(self):
        messages_sent = 10
        for i in range(messages_sent):
            self.send_message("Message")

        rv = self.get_all_msgs()
        actual_msgs_sent= json.loads(rv.data)

        self.assertEqual(len(actual_msgs_sent),messages_sent)

        for msg in actual_msgs_sent:
            self.assertEqual(msg["message"],"Message")





    def get_all_msgs(self):
        return self.app.get('/messages')

    def send_message(self, message):
        return self.app.post('/messages', data = json.dumps(dict(message=message)),content_type="application/json" )

if __name__ == '__main__':
    unittest.main()