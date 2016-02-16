#!/usr/bin/env python
import os

from lab2 import app as application

virtenv = os.path.join(os.environ.get('OPENSHIFT_PYTHON_DIR','.'), 'virtenv')

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 80, application)
    httpd.serve_forever()
