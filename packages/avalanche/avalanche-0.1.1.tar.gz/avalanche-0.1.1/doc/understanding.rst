===================================
Tutorial - Understanding Avalanche
===================================

This is a tutorial for a very simple *task list* application.
It is based on `Pyramid Single File Tasks Tutorial <http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/single_file_tasks/single_file_tasks.html>`_.
This tutorial assumes you have some basic knowledge of web development
(HTTP, HTML, CSS) and python.

Avalanche relies on `webapp2 <http://webapp-improved.appspot.com/>`_,
`webob <http://docs.webob.org/>`_ and `Jinja2 <http://jinja.pocoo.org/>`_.
So you should be familiar with those in order to use Avalanche.
This tutorial will not cover them.
If you have used any other WSGI framework good chances you can follow
this tutorial even if you had never looked at webapp2.
This tutorial application is based on `Google AppEngine <http://code.google.com/appengine/docs/python/gettingstartedpython27/>`_.
So for this tutorial you should also be familiar with it.

The goal of this tutorial is to let you understand how Avalanche
works and its design. It is not just a "getting started" or "user's tutorial",
it will expose some internals that the user are not required to have knowledge of.

In this tutorial instead of starting from scratch we will start with the
application written using webapp2.
From that we will refactor the code using Avalanche to satisfy some
reusability use-cases and to improve the tests.
It is widely recognized the correlation that testable code leads to well
modularized, and reusable code.



Setup
=========

If you want to run the application locally first download the `AppEngine SDK <http://code.google.com/appengine/downloads.html>`_ 1.6.3 or later. Create a virtualenv as described `here <http://schettino72.wordpress.com/2010/11/21/appengine-virtualenv/>`_. (but you should use python2.7)

The complete code for this application and all steps can be found on avalanche `repository <https://bitbucket.org/schettino72/avalanche>`_ in the folder `avalanche/doc/tutorial/tasks`.


Step 0
========

On this step the code is using plain webapp2, not using Avalanche yet.

app.yaml
----------

This is the configuration file used by AppEngine.

`app.yaml`

.. literalinclude:: tutorial/tasks/app.yaml


basehandler.py
----------------

webapp2 is a very simple framework but allows you to easily add optional features.
These optional features can be added by sub-classing webapp2.RequestHandler.
In this tutorial we will use Jinja2 to render templates and sessions.
webapp2_extras already provides utility code for these (`jinja <http://webapp-improved.appspot.com/api/webapp2_extras/jinja2.html>`_, `sessions <http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html>`_), so all we need to do is to assemble them to together...

There is also a customization of the exception handler to display the traceback when an internal error occurs.

`basehandler.py`

.. literalinclude:: tutorial/tasks/basehandler.py


tasks.py
----------


Model
++++++++

The application contains a single model class. Each `Task` has a `name`,
a boolean property `closed` to indicated if the Task has been completed.
And timestamp of when the task was `created`.

.. code-block:: python

  from google.appengine.ext import db

  class Task(db.Model):
      name = db.StringProperty(required=True)
      closed = db.BooleanProperty(default=False)
      created = db.DateTimeProperty(auto_now_add=True)


TaskBaseHandler
+++++++++++++++++

``TaskRequestHandler`` will be used as base class for all the handlers in the Task application.
It subclass from ``BaseHandler`` to get support for session and a Jinja2 renderer.
Apart from that it just add some string messages that will be used by the application.

.. code-block:: python

  from basehandler import BaseHandler


  class TaskRequestHandler(BaseHandler):

      MSG_TASK_NEW = 'New task successfully added'
      MSG_TASK_NAME = 'Please enter a name for the task'
      MSG_TASK_CLOSED = 'Task was successfully closed'


ListTasks
+++++++++++

This handler will display the initial page with a list of tasks.
It has an option to display all tasks or just the ones that are not completed.

.. code-block:: python

  class ListTasks(TaskRequestHandler):
      """list all open tasks"""
      def get(self):
          show_closed = self.request.get('closed')
          if show_closed:
              tasks = Task.all().order('created')
          else:
              tasks = Task.all().filter('closed = ', False).order('created')
          flash = self.session.get_flashes()
          self.render_response('task_list.html', tasks=tasks, flash=flash,
                               show_closed=show_closed)


NewTask
+++++++++

This handler will display a form to create a new task.
The ``post`` method creates a new Task instance and saves it into the datastore.
It also adds a message into the session to be flashed out on the next page view.

.. code-block:: python

  class NewTask(TaskRequestHandler):
      """add a new task"""
      def get(self):
          flash = self.session.get_flashes()
          self.render_response('task_new.html', flash=flash)

      def post(self):
          name = self.request.get('task-name')
          if name:
              Task(name=name).put()
              self.session.add_flash(self.MSG_TASK_NEW)
              self.redirect(self.uri_for('task-list'))
          else:
              self.session.add_flash(self.MSG_TASK_NAME)
              self.redirect(self.uri_for('task-new'))


CloseTask
+++++++++++

This handler's ``post`` method will modify a task marking it as closed.

.. code-block:: python

  class CloseTask(TaskRequestHandler):
      """mark a task as closed"""
      def post(self, task_id):
          task = Task.get_by_id(int(task_id))
          task.closed = True
          task.put()
          self.session.add_flash(self.MSG_TASK_CLOSED)
          self.redirect(self.uri_for('task-list'))


WSGI App
++++++++++++++++

Create a WSGI application mapping URI's to handlers and adding some config values.

.. code-block:: python

  import webapp2

  def tasks_app():
      routes = [
          webapp2.Route('/', ListTasks, name='task-list'),
          webapp2.Route('/new', NewTask, name='task-new'),
          webapp2.Route('/close/<task_id>', CloseTask, name='task-close'),
          ]
      config = {}
      config['webapp2_extras.sessions'] = {'secret_key': '1234567890'}
      config['webapp2_extras.jinja2'] = {'globals': {'uri_for': webapp2.uri_for}}

      return  webapp2.WSGIApplication(routes, debug=True, config=config)


  app = tasks_app()



Complete source for step 0 `tasks_0.py <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_0.py>`_



templates
----------

Create a folder name `templates` and the three Jinja template files. We won't go through the templates in this tutorial.

`base.html`

.. literalinclude:: tutorial/tasks/templates/base.html


`task_list.html`

.. literalinclude:: tutorial/tasks/templates/task_list.html


`task_new.html`

.. literalinclude:: tutorial/tasks/templates/task_new.html



static
-------

Create a folder named `static` and add the CSS file:

`task.css`

.. literalinclude:: tutorial/tasks/static/task.css


running the application
-------------------------

Now you should be able to run the application:

.. code-block:: console

  (gae)~/tasks$ dev_appserver.py --datastore_path dev.db .


Step 0 - Tests
================

The tests are going to use `pytest <http://pytest.org>`_ as unit-test framework and `WebTest <http://pypi.python.org/pypi/WebTest>`_ (a helper to test WSGI applications). To install them:

.. code-block:: console

 (gae)~/tasks$ pip install pytest webtest


`tests/test_tasks.py`

.. literalinclude:: tutorial/tasks/tests/test_tasks_0.py

`pytest_funcarg__app` is a `pytest funcarg <http://pytest.org/latest/funcargs.html>`_,
this is an alternative (and better) approach instead of using xUnit test `setUp` and `tearDown` methods.
In this case the `funcarg` will create a WSGI application and use `testbed <http://code.google.com/appengine/docs/python/tools/localunittesting.html>`_ to reset the datastore for every test.

The tests are pretty straight forward to write. Basically they:
  1) add some test data into the datastore
  2) send a HTTP request to the application
  3) check the HTML of the response
  4) check the datastore


Problems
-----------

But these are very bad unit-tests.
Most of the problems come from checking the HTML response. These are actually
black-box testing, unit-test by definition are white-box testing.


* writing tests is error prone

  When you write a check for a string in a HTML document you expect that string to
  be in a determined position. If this same string happens to appear in a different
  position by another part of your page you are actually not testing anything. This
  is much more common that might seems at first.

  Another problem is negative testing, that is testing that a page does not
  contains a string.
  This kind of test always pass when you get a blank page, and this is
  hardly ever what you expect.


* no clear error message when test fails

  Its normal that unit-tests will eventually fail, when it does it should be easy
  for the developer to pin-point what went wrong.

  When test assertion fails it should tell you what value was expected
  and what it got.
  Testing a for a string in a web-page you will just get the whole HTML text.
  From the HTML text you will have to find the position where you expected the
  text to be and check what was the actual/incorrect output.
  This can be quite time consuming and annoying.

  Another problem is that it impossible to tell in which stage things did not
  run as expected.
  In other words you can only write asserts for the final output.


* test breaks too easily

  A unit-test should fail only when the feature under test is broken.
  A page often contain several components/parts, sometimes a problem will
  break other unrelated tests. This also makes it harder to pin-point where is the
  problem.


* tests are slower than necessary

  The tests get slower because the application has to process components/parts
  of the page that are not under test.

  Another reason is that checking for a string or regular expression in a text
  is much slower than a direct value comparison/assertion.


Step 1
========

.. topic:: Reusability use-case 1

   Re-use a request handler using a different renderer

One problem of the original code is that the handler will directly render
the jinja template. The goal is to make it possible to re-use the same handler
logic but using a different template system or a different template.


avalanche.py
--------------

Avalanche code is a single module. Add it to your project folder `(avalanche.py source) <https://bitbucket.org/schettino72/avalanche/src/tip/avalanche.py>`_


avalanche.CoreHandler
-----------------------

``avalanche.CoreHandler`` is a `mixin <http://en.wikipedia.org/wiki/Mixin>`_
to be used with a ``webapp2.RequestHandler``. Actually this `avalanche.CoreHandler` is
supposed to be used only internally by Avalanche, we will actually remove
it from the code in the next step.

So first lets make ``TaskRequestHandler`` a subclass from `avalanche.CoreHandler`
(and BaseHandler).

.. code-block:: diff

  + import avalanche
  - class TaskRequestHandler(BaseHandler):
  + class TaskRequestHandler(avalanche.CoreHandler, BaseHandler):


If you run the code you wont notice any difference!
The CoreHandler provides a different style/abstraction to code your handlers.
But you are not strictly required to follow it.


The main role of `avalanche.CoreHandler` is to divide the work done
by the `get/post` handler methods into different stages.
By default ``CoreHandler.get`` will call the method ``a_get`` that is supposed
to return a dictionary with the context data to be used by the renderer.
And than write renderer output into the response.

Since ``ListTasks`` also defines a ``get`` method the ``CoreHandler.get`` is
not being used.


render & Jinja2 renderer
+++++++++++++++++++++++++

CoreHandler has a method ``render`` that takes a a dictionary parameter as
the context data to render a Jinja2 `template`.
The template must be located at a `templates` dictionary.
The Jinja renderer is a class variable ``renderer``.

get
+++++

When using avalanche instead of writing the ``get`` method you should write a
`context-builder` method. By default this context-builder is called ``a_get``.

.. code-block:: diff

    class ListTasks(TaskRequestHandler):
        """list all open tasks"""
  +     template = 'task_list.html'
  -     def get(self):
  +     def a_get(self):
            show_closed = self.request.get('closed')
            if show_closed:
                tasks = Task.all().order('created')
            else:
                tasks = Task.all().filter('closed = ', False).order('created')
            flash = self.session.get_flashes()
  -         self.render_response('task_list.html', tasks=tasks, flash=flash,
  -                              show_closed=show_closed)
  +         return {'tasks': tasks,
  +             'flash': flash,
  +             'show_closed': show_closed,
  +             }


post
++++++

Similarly for handling a HTTP ``post`` you should write ``a_post`` method.
This is different from ``get`` because the renderer is not called by default
(post response usually should redirect, see `post-redirect-get <http://en.wikipedia.org/wiki/Post/Redirect/Get>`_).


Changes to the other handlers:

.. code-block:: diff

    class NewTask(TaskRequestHandler):
        """add a new task"""
  +     template = 'task_new.html'
  -     def get(self):
  +     def a_get(self):
            flash = self.session.get_flashes()
  -         self.render_response('task_new.html', flash=flash)
  +         return {flash=flash}


  -     def post(self):
  +     def a_post(self):
            name = self.request.get('task-name')
            if name:
                Task(name=name).put()
                self.session.add_flash(self.MSG_TASK_NEW)
                self.redirect(self.uri_for('task-list'))
            else:
                self.session.add_flash(self.MSG_TASK_NAME)
                self.redirect(self.uri_for('task-new'))


    class CloseTask(TaskRequestHandler):
        """mark a task as closed"""
  -     def post(self, task_id):
  +     @avalanche.url_path_param('task_id')
  +     def a_post(self, task_id):
            task = Task.get_by_id(int(task_id))
            task.closed = True
            task.put()
            self.session.add_flash(self.MSG_TASK_CLOSED)
            self.redirect(self.uri_for('task-list'))

Basically it is just removing the rendering of the HTML from the context builder
and letting the framework do it.
The decorator on ``CloseTask.a_post`` will be explained later,
for now just copy it.

Complete source of `tasks.py step 1 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_1.py>`_


step 1 - tests
-----------------

Now it is possible to test our handler's `context-builder` method directly.
First lets change our imports, it will not require to use WebTest anymore.

.. code-block:: diff

  - from webtest import TestApp
  + from urlparse import urlparse


  + from webapp2 import Request, Response

  + from tasks import ListTasks, NewTask, CloseTask


    # create test app
    def pytest_funcarg__app(request):
        def create():
            my_testbed = testbed.Testbed()
            my_testbed.activate()
            my_testbed.init_datastore_v3_stub()

  -         app = TestApp(tasks_app())
  +         app = tasks_app()
            app.testbed = my_testbed
            return app


We still need to create a WSGI app for our tests because the app manages a
reference to Jinja2 and session environment.

The tests now will use the request handlers directly.
So we need to manually create and setup the handlers
(this is usually done by the app during the dispatch process).
Here is a helper function for that.

.. code-block:: diff

    + def create_handler(app, handler_class, path='', POST=None, **req_kwargs):
    +     """helper to setup request handler instances"""
    +     request = Request.blank(path, POST=POST, **req_kwargs)
    +     request.app = app
    +     handler = handler_class(request, Response())
    +     handler._make_session_store()
    +     return handler


And here are the changes on ``TestListTasks``:

.. code-block:: diff

      class TestListTasks(object):
          def test_get_display_not_closed(self, app):
              Task(name='my first task').put()
              Task(name='task 2', closed=True).put()
              Task(name='task 3').put()

    -         response = app.get('/')
    -         assert "Task's List" in response
    -         assert "show closed" in response
    -         assert "my first task" in response
    -         assert "task 2" not in response
    -         assert "task 3" in response
    +         handler = create_handler(app, ListTasks)
    +         handler.session.add_flash('flash message')
    +         ctx = handler.a_get()
    +         tasks = list(ctx['tasks'])
    +         assert len(tasks) == 2 # closed task is not included
    +         assert tasks[0].name == "my first task"
    +         assert tasks[1].name == "task 3"
    +         assert ctx['flash'] == [('flash message', None)]
    +         assert bool(ctx['show_closed']) == False


Note that we are not testing the template anymore. And that's exactly what we want!


Since the handler contains a response object we can assert the HTTP-redirect was correct:

.. code-block:: diff

    class TestNewTask(object):

        def test_post_save(self, app):
  -         response_0 = app.post('/new', {'task-name':'task test xxx'})
  +         post_data = {'task-name':'task test xxx'}
  +         handler = create_handler(app, NewTask, POST=post_data)
  +         handler.a_post()

            # task is saved in DB
            saved = Task.all().get()
            assert saved
            assert 'task test xxx' == saved.name

            # page is redirected to list page
  -         response = response_0.follow()
  -         assert "Task's List" in response
  +         assert handler.response.status_int == 302
  +         assert urlparse(handler.response.location).path == handler.uri_for('task-list')

            # flash message in page
  -         assert TaskRequestHandler.MSG_TASK_NEW in response
  +         assert handler.session.get_flashes()[0][0] == TaskRequestHandler.MSG_TASK_N


You can check the other changes from the complete source of `tests step 1 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_1.py>`_



Step 2
========

.. topic:: Reusability use-case 2

   Re-use a request handler in a different application (different BaseHandler)


Our application handlers (``ListTasks``) are sub-classes from ``BaseHandler``.
This makes it easy to write code because we get access to all BaseHandler features.
But the problem is that different applications use different BaseHandler's.
So to make it reusable there should be an intermediate class so that the
application handlers do not directly subclass from ``BaseHandler``.

The application handlers still need to subclass from ``AvalancheHandler``.
``AvalancheHandler`` is important for the configuration system,
the configuration system will be explained later.

.. code-block:: diff

  - class TaskRequestHandler(avalanche.CoreHandler, BaseHandler):
  + class TaskRequestHandler(avalanche.AvalancheHandler):

    class ListTasks(TaskRequestHandler):

  + class ListTasksHandler(ListTasks, avalanche.CoreHandler, BaseHandler):
  +     pass


       routes = [
  -       webapp2.Route('/', ListTasks, name='task-list'),
  +       webapp2.Route('/', ListTasksHandler, name='task-list'),


Now it easier to reuse the handler in a different application.
But note that the user is responsible to ensure that
the BaseHandler being used has all features required by the application handler.

Creating an intermediate class for every handler would be very annoying.
Luckily in python it is very easy to create new types/classes dynamically.


.. code-block:: diff

  - class ListTasksHandler(ListTasks, avalanche.CoreHandler, BaseHandler):
  -     pass
  + ListTasksHandler = type('ListTasksHandler', (ListTasks, avalanche.CoreHandler, BaseHandler), {})

Avalanche comes with a function to that for you, ``make_handler``.
Putting all together:

.. code-block:: diff

  - class TaskRequestHandler(avalanche.CoreHandler, BaseHandler):
  + class TaskRequestHandler(avalanche.AvalancheHandler):


  -   routes = [
  -       webapp2.Route('/', ListTasks, name='task-list'),
  -       webapp2.Route('/new', NewTask, name='task-new'),
  -       webapp2.Route('/close/<task_id>', CloseTask, name='task-close'),
  -       ]

  +   route_raw = [('/', ListTasks, 'task-list'),
  +                ('/new', NewTask, 'task-new'),
  +                ('/close/<task_id>', CloseTask, 'task-close')
  +                ]
  +   routes = []
  +   for path, handler, name in route_raw:
  +       handler_class = avalanche.make_handler(BaseHandler, handler)
  +       routes.append(webapp2.Route(path, handler_class, name))


Complete source of `tasks.py step 2 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_2.py>`_


step 2 - tests
----------------

The tests are not modified. We just need to adjust how the handlers are created.

.. code-block:: diff

  +  import avalanche

  +  from basehandler import BaseHandler


  -  def create_handler(app, handler_class, path='', POST=None, **req_kwargs):
  +  def create_handler(app, app_class, path='', POST=None, **req_kwargs):
        """helper to setup request handler instances"""
        request = Request.blank(path, POST=POST, **req_kwargs)
        request.app = app
  +     handler_class = avalanche.make_handler(BaseHandler, app_class)
        handler = handler_class(request, Response())
        handler._make_session_store()
        return handler


Complete source of `tests step 2 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_2.py>`_


step 3
========

.. topic:: Reusability use-case 3

   Re-use a `context-builder` in more than one request handler


Looking at our application pages we can see that all pages are composed of
two parts or sections. The section containing the flash message and the main
content of the page.

Of course repeating the code for the flash message on every handler is not good practice.
Avalanche supports the definition of more than one `context-builder` in
each handler, thus facilitating code re-use.
Since this is common to all handlers we will add it to `TaskRequstHandler`.


.. code-block:: diff

    class TaskRequestHandler(avalanche.AvalancheHandler):

        MSG_TASK_NEW = 'New task successfully added'
        MSG_TASK_NAME = 'Please enter a name for the task'
        MSG_TASK_CLOSED = 'Task was successfully closed'

  +     context_get = ['a_get', 'ctx_flash',]
  +
  +     def ctx_flash(self):
  +         flash = self.session.get_flashes()
  +         return {'flash': flash}


The class variable ``context_get`` contains a list of strings with the name
of the methods that are `context-builders`. By default it has a single element
`a_get`. Here we create a `context-builder` called `ctx-flash` and add it to
the list of builders.

After that we can remove the repeated code from the handlers dealing with the
retrieval of the flash messages.

.. code-block:: diff

    class ListTasks(TaskRequestHandler):
        """list all open tasks"""
        template = 'task_list.html'

        def a_get(self):
            show_closed = bool(self.request.get('closed'))
            if show_closed:
                tasks = Task.all().order('created')
            else:
                tasks = Task.all().filter('closed = ', False).order('created')
   -        flash = self.session.get_flashes()
            return {'tasks': tasks,
   -                'flash': flash,
                    'show_closed': show_closed,
                    }

    class NewTask(TaskRequestHandler):
        """add a new task"""
        template = 'task_new.html'

        def a_get(self):
   -        flash = self.session.get_flashes()
   -        return {'flash': flash}
   +        pass


Complete source of `tasks.py step 3 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_3.py>`_


Step 3 - tests
---------------

Our tests are actually testing the flash functionality several times.
This is bad not only because of the code repetition but also because it adds up
on the time taken to execute the tests.
Another problem is that a single error could break many tests.

.. code-block:: diff

  + class TestTaskRequestHandler(object):
  +     def test_ctx_flash(self, app):
  +         handler = create_handler(app, ListTasks)
  +         handler.session.add_flash('flash message')
  +         ctx = handler.ctx_flash()
  +         assert ctx['flash'] == [('flash message', None)]


    class TestListTasks(object):
        def test_get_display_not_closed(self, app):
            Task(name='my first task').put()
            Task(name='task 2', closed=True).put()
            Task(name='task 3').put()

            handler = create_handler(app, ListTasks)
  -         handler.session.add_flash('flash message')
            ctx = handler.a_get()
            tasks = list(ctx['tasks'])
            assert len(tasks) == 2 # closed task is not included
            assert tasks[0].name == "my first task"
            assert tasks[1].name == "task 3"
  -         assert ctx['flash'] == [('flash message', None)]
            assert ctx['show_closed'] == False

        def test_get_display_all(self, app):
            Task(name='my first task').put()
            Task(name='task 2', closed=True).put()
            Task(name='task 3').put()

            handler = create_handler(app, ListTasks, '?closed=1')
  -         handler.session.add_flash('flash message')
            ctx = handler.a_get()
            tasks = list(ctx['tasks'])
            assert len(tasks) == 3
            assert tasks[0].name == "my first task"
            assert tasks[1].name == "task 2"
            assert tasks[2].name == "task 3"
  -         assert ctx['flash'] == [('flash message', None)]
            assert ctx['show_closed'] == True


    class TestNewTask(object):
        def test_get(self, app):
  -         handler = create_handler(app, NewTask)
  -         handler.session.add_flash('flash message')
  -         ctx = handler.a_get()
  -         assert ctx['flash'][0][0] == 'flash message'
  +         pass


Complete source of `tests step 3 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_3.py>`_


step 4
========

.. topic:: Reusability use-case 4

   Re-use a `context-builder` from a different request handler

In the previous step we added the `context-builder` for flash messages into
`TaskRequestHandler`.
Flash messages are a quite generic, so the goal now is to make it easier to re-use
that in other RequestHandlers that do not subclass from `TaskRequestHandler`.

The solution is trivial. We just need to put the `ctx_flash` in a mixin.

.. code-block:: diff

  + class FlashMixinHanlder(avalanche.AvalancheHandler):
  +     def ctx_flash(self):
  +         flash = self.session.get_flashes()
  +         return {'flash': flash}

  - class TaskRequestHandler(avalanche.AvalancheHandler):
  + class TaskRequestHandler(FlashMixinHandler, avalanche.AvalancheHandler):

        MSG_TASK_NEW = 'New task successfully added'
        MSG_TASK_NAME = 'Please enter a name for the task'
        MSG_TASK_CLOSED = 'Task was successfully closed'

        context_get = ['a_get', 'ctx_flash',]

  -     def ctx_flash(self):
  -         flash = self.session.get_flashes()
  -         return {'flash': flash}

Complete source of `tasks.py step 4 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_4.py>`_

step 4 - tests
----------------

No real advantage from the point of view of tests.

.. code-block:: diff

  + from tasks import FlashMixinHandler

  - class TestTaskRequestHandler(object):
  + class TestFlashMixinHandler(object):
        def test_ctx_flash(self, app):
  -         handler = create_handler(app, ListTasks)
  +         handler = create_handler(app, FlashMixinHandler)
            handler.session.add_flash('flash message')
            ctx = handler.ctx_flash()
            assert ctx['flash'] == [('flash message', None)]

Complete source of `tests step 4 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_4.py>`_


step 5
========

.. topic:: Reusability use-case 5

   Re-use `context-builder` (remove dependency on request object)

One thing that makes it harder to re-use a `context-builder` is its dependency
on the request object.
Avalanche has some decorators used to configure the `context-builder` methods
to indicate from where the method arguments should be taken from.

For example one handler might take parameter from a url query string.
But a different handler might need the same context but taking the parameter
from the url path, or from a session.
Another reason is that a `context-builder` not accessing a request might be used
from within another function (not directly by the framework).


param from url query string
----------------------------

``url_query_param`` takes its value from the URL query string.
It takes 3 arguments:

 * name of the parameter in the `context-builder` method
 * name of the parameter in URL query (optional if name is same as above)
 * a function that takes a string and returns any python object (optional)

.. code-block:: diff

    class ListTasks(TaskRequestHandler):
        """list all open tasks"""
        template = 'task_list.html'

   -    def a_get(self):
   -        show_closed = bool(self.request.get('closed'))
   +    @avalanche.url_query_param('show_closed', 'closed', bool)
   +    def a_get(self, show_closed):
            if show_closed:


param from POST data
----------------------

``post_group_param`` decorator creates a dictionary with all POSTed data
that has a given prefix (separated by '-'). arguments:

 * name of the parameter in the `context-builder` method
 * name of the prefix in the POSTed data

.. code-block:: diff

    class NewTask(TaskRequestHandler):
        """add a new task"""
        template = 'task_new.html'

  -    def a_post(self):
  -         name = self.request.get('task-name')
  +    @avalanche.post_group_param('data', 'task')
  +    def a_post(self, data):
  +         name = data.get('name')
            if name:
                Task(name=name).put()


param from URL path
---------------------

``url_path_param`` is similar to ``url_query_param`` but it's value is taken
from the router.

We will also move the logic of retrieving a task entity from the datastore from
the handler to the model.


.. code-block:: diff

    class Task(db.Model):
        name = db.StringProperty(required=True)
        closed = db.BooleanProperty(default=False)
        created = db.DateTimeProperty(auto_now_add=True)

  +     @staticmethod
  +     def id2task(task_id):
  +         """@param task_id: (str)"""
  +         return Task.get_by_id(int(task_id))


    class CloseTask(TaskRequestHandler):
        """mark a task as closed"""

  -    @avalanche.url_path_param('task_id')
  -    def a_post(self, task_id):
  -         task = Task.get_by_id(int(task_id))
  +     @avalanche.url_path_param('task', 'task_id', Task.id2task)
  +     def a_post(self, task):
            task.closed = True
            task.put()
            self.session.add_flash(self.MSG_TASK_CLOSED)
            self.redirect(self.uri_for('task-list'))


Complete source of `tasks.py step 5 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_5.py>`_



step 5 - tests
----------------

Test for the new method on Task model.

.. code-block:: diff

  + class TestTaskModel(object):
  +     def test_id2task(self, app):
  +         task_key = Task(name='my first task').put()
  +         got = Task.id2task(str(task_key.id()))
  +         assert task_key == got.key()


And change the tests to pass the parameters diretcyl to the context-builders.

.. code-block:: diff

    def test_get_display_not_closed(self, app):
        Task(name='my first task').put()
        Task(name='task 2', closed=True).put()
        Task(name='task 3').put()

        handler = create_handler(app, ListTasks)
  -     ctx = handler.a_get()
  +     ctx = handler.a_get(show_closed=False)
        tasks = list(ctx['tasks'])


.. code-block:: diff

    def test_get_display_all(self, app):
        Task(name='my first task').put()
        Task(name='task 2', closed=True).put()
        Task(name='task 3').put()

  -     handler = create_handler(app, ListTasks, '?closed=1')
  +     handler = create_handler(app, ListTasks)
  -     ctx = handler.a_get()
  +     ctx = handler.a_get(show_closed=True)
        tasks = list(ctx['tasks'])

.. code-block:: diff

    def test_post_save(self, app):
  -     post_data = {'task-name':'task test xxx'}
  -     handler = create_handler(app, NewTask, POST=post_data)
  +     handler = create_handler(app, NewTask, POST={})
  -     handler.a_post()
  +     handler.a_post(data={'name': 'task test xxx'})

        # task is saved in DB
        saved = Task.all().get()

.. code-block:: diff

    def test_post_error(self, app):
  -     post_data = {'wrong-name': 'task test xxx'}
  -     handler = create_handler(app, NewTask, POST=post_data)
  +     handler = create_handler(app, NewTask, POST={})
  -     handler.a_post()
  +     handler.a_post(data={'wrong-name': 'task test xxx'})

        # task is not saved in DB
        saved = Task.all().get()


.. code-block:: diff

   class TestCloseTask(object):
       def test_post(self, app):
           task_before = Task(name="task abc")
           task_before.put()
           assert not task_before.closed

           handler = create_handler(app, CloseTask, POST={})
  -        handler.a_post(str(task_before.key().id())
  +        handler.a_post(task_before)

           # task is closed
           task_after = Task.get_by_id(task_before.key().id())

Complete source of `tests step 5 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_5.py>`_


step 6
========

This final step will not introduce any new use-case or avalanche concept.
But there is one last thing that should be refactored.
All flash messages are being directly saved by the handlers, this would make it
hard to re-use the handlers in another application that uses a different
session storage.

We will modify the POST methods to save the flash messages in the context.
And add context-builder in FlashMixinHandler to actually add the messages to
the session.

``context_param`` is used to take a value from the context.


.. code-block:: diff

   class FlashMixinHandler(avalanche.AvalancheHandler):
       def ctx_flash(self):
           flash = self.session.get_flashes()
           return {'flash': flash}

 +     @avalanche.context_param('messages', 'flash')
 +     def add_flash(self, messages):
 +         for msg in messages:
 +             self.session.add_flash(msg)


   class TaskRequestHandler(FlashMixinHandler, avalanche.AvalancheHandler):

       MSG_TASK_NEW = 'New task successfully added'
       MSG_TASK_NAME = 'Please enter a name for the task'
       MSG_TASK_CLOSED = 'Task was successfully closed'

       context_get = ['a_get', 'ctx_flash',]
 +     context_post = ['a_post', 'add_flash',]


.. code-block:: diff

   class NewTask(TaskRequestHandler):

       @avalanche.post_group_param('data', 'task')
       def a_post(self, data):
 +         ctx = {'flash': []}
           name = data.get('name')
           if name:
               Task(name=name).put()
 -             self.session.add_flash(self.MSG_TASK_NEW)
 +             ctx['flash'].append(self.MSG_TASK_NEW)
               self.redirect(self.uri_for('task-list'))
           else:
 -             self.session.add_flash(self.MSG_TASK_NAME)
 +             ctx['flash'].append(self.MSG_TASK_NAME)
               self.redirect(self.uri_for('task-new'))
 +         return ctx

   class CloseTask(TaskRequestHandler):
       """mark a task as closed"""

       @avalanche.url_path_param('task', 'task_id', Task.id2task)
       def a_post(self, task):
 +         ctx = {'flash': []}
           task.closed = True
           task.put()
 -         self.session.add_flash(self.MSG_TASK_CLOSED)
 +         ctx['flash'].append(self.MSG_TASK_CLOSED)
           self.redirect(self.uri_for('task-list'))
 +         return ctx

Complete source of `tasks.py step 6 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_6.py>`_


step 6 - tests
----------------

.. code-block:: diff

   class TestFlashMixinHandler(object):

 +     def test_add_flash(self, app):
 +         handler = create_handler(app, FlashMixinHandler)
 +         handler.add_flash(['flash message'])
 +         assert handler.session.get_flashes()[0][0] == 'flash message'


.. code-block:: diff

       def test_post_save(self, app):
           handler = create_handler(app, NewTask, POST={})
 -         handler.a_post(data={'name': 'task test xxx'})
 +         ctx = handler.a_post(data={'name': 'task test xxx'})

           # task is saved in DB
           saved = Task.all().get()
           assert saved
           assert 'task test xxx' == saved.name

           # page is redirected to list page
           assert handler.response.status_int == 302
           assert urlparse(handler.response.location).path == handler.uri_for('task-list')

           # flash message in page
  -        assert handler.session.get_flashes()[0][0] == TaskRequestHandler.MSG_TASK_NEW
  +        assert ctx['flash'][0] == TaskRequestHandler.MSG_TASK_NEW


You can check the other changes from the complete source of `tests step 6 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_6.py>`_


Other use cases
=================

This first release of Avalanche focus on getting re-usability of single
RequestHandler's separetely.
Next releases will focus on re-usability of several handlers at once.
