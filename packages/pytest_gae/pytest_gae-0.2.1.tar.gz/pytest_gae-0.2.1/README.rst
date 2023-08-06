pytest_gae
==========

It is `pytest <http://pytest.org/>`_ plugin that helps You to test
applications written with Google's `AppEngine
<http://code.google.com/appengine/>`_.


Options
=======

- --with-gae: Turns on this plugin
- --gae-path: AppEngine's root (default *google_appengine*)
- --gae-project-path: Your project's root (default *./*)


Limitation
==========


Plugin does not prevent You from using code/modules that AppEngine's
environment refuse to execute. So, You can easily do something like that::

  import socket
  import numpy

And tests just pass. But You can not run this code on AppEngine environment,
because of sandboxing. See: `AppEngine Docs
<http://code.google.com/appengine/docs/python/runtime.html>`_

This plugin uses internal AppEngine's code and there is no guarantee that
Google is not going to change it.


Others
======

This project was inspired by nose-gae plugin for nose

`http://code.google.com/p/nose-gae/ <http://code.google.com/p/nose-gae/>`_


Usage example
=============

Let assume we have a directory that looks something like that ::

  ./
  |-- gae               # AppEngine's root
  |   |-- ...
  |-- src               # Your project's root
  |   |-- app.yaml
  |   |-- index.yaml
  |   |-- main.py
  |-- tests             # Tests' dir
      |-- test_handlers.py
      |-- test_models.py


main.py::

  #!/usr/bin/env python
  from google.appengine.ext import webapp
  from google.appengine.ext.webapp import util
  from google.appengine.ext.webapp.util import login_required
  from google.appengine.api import users
  from google.appengine.ext import db


  class MyModel(db.Model):
      my_field = db.StringProperty(required=False)


  class IndexHandler(webapp.RequestHandler):
      def get(self):
          self.response.out.write('Index')


  class UsersHandler(webapp.RequestHandler):

      @login_required
      def get(self):
          if users.is_current_user_admin():
              self.response.out.write('Admin')
          else:
              self.response.out.write('User')


  def make_application():
      return webapp.WSGIApplication([('/index', IndexHandler),
                                     ('/users', UsersHandler)], debug=True)


  def main():
      application = make_application()
      util.run_wsgi_app(application)


  if __name__ == '__main__':
      main()

Testing models
--------------

test_models.py::

  from google.appengine.ext import db
  import pytest

  from main import MyModel


  def test_basic():
      m = MyModel(my_field='Foo')
      assert 'Foo' == m.my_field


  def test_new_model():
      m = MyModel(my_field='Foo')
      pytest.raises(db.NotSavedError, lambda: m.key())


  def test_saved_model():
      m = MyModel(my_field='Foo')
      m.put()
      assert m.key()


Using with WebTest
------------------

We could test our handlers with the help of `WebTest
<http://pythonpaste.org/webtest/>`_ library.


We would create three funcargs' functions that allows us to test application:

- From anonymous user perspective
- From authorized user perspective
- From admin perspective

We could do that by altering *os.enviroment*


test_handlers.py::

  import os

  from webtest import TestApp
  from main import make_application


  def pytest_funcarg__anon_app(request):
      os.environ.update({'USER_EMAIL': '',
                          'USER_ID': '',
                          'AUTH_DOMAIN': 'google',
                          'USER_IS_ADMIN': '0'})
      return TestApp(make_application())


  def pytest_funcarg__user_app(request):
      os.environ.update({'USER_EMAIL': 'simple@google.com',
                         'USER_ID': '1',
                         'AUTH_DOMAIN': 'google',
                         'USER_IS_ADMIN': '0'})
      return TestApp(make_application())


  def pytest_funcarg__admin_app(request):
      os.environ.update({'USER_EMAIL': 'admin@google.com',
                         'USER_ID': '2',
                         'AUTH_DOMAIN': 'google',
                         'USER_IS_ADMIN': '1'})
      return TestApp(make_application())


  def test_index(anon_app):
      assert "Index" in anon_app.get('/index')


  def test_user_with_user(user_app):
      assert "User" in user_app.get('/users')


  def test_user_with_anon(anon_app):
      assert '302 Moved Temporarily' == anon_app.get('/users').status


  def test_user_with_admin(admin_app):
      assert "Admin" in admin_app.get('/users')

Running
-------

::

  py.test tests --with-gae --gae-path=gae --gae-project-path=./src/ :
  platform linux2 -- Python 2.5.5 -- pytest-2.0.0
  collected 7 items

  tests/test_handlers.py ....
  tests/test_models.py ...

  ============ 7 passed in 0.64 seconds ============
