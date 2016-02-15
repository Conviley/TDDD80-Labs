from setuptools import setup

setup(name='YourAppName',
      version='1.0',
      description='OpenShift App',
      author='Tjelvar Guo',
      author_email='tjegu689@student.liu.se',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['Flask','Flask-SQLAlchemy>=2.1', "sqlalchemy>=1.0.11"],
     )
