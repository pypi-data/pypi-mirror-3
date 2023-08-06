===================================
Tutorial - Understanding Avalanche
===================================

This is a tutorial for a very simple *task list* application.
It is based on `Pyramid Single File Tasks Tutorial <http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/single_file_tasks/single_file_tasks.html>`_.
This tutorial assumes you have some basic knowledge of web development
(HTTP, HTML, CSS) and python.

Avalanche relies on `webob <http://docs.webob.org/>`_ for HTTP (WSGI)
Request/Response objects.

Avalanche is composed of two main parts. The `core` contains a very basic
WSGI framework based on `webapp2 <http://webapp-improved.appspot.com/>`_.
This `core` contains a WSGI application, a class-based RequestHandler and
URL routing.

Avalanche itself is built on top of this `core` framework to provide extra
functionality. It uses `Jinja2 <http://jinja.pocoo.org/>`_ as a template language
(you should be familiar with Jinja2, this tutorial will not cover it).

This tutorial application is based on
`Google AppEngine <http://code.google.com/appengine/docs/python/gettingstartedpython27/>`_.
So for this tutorial you should also be familiar with it.

The goal of this tutorial is to let you understand how Avalanche
works and its design. It is not just a "getting started" or "user's tutorial",
it will expose some internals that the user are not required to have knowledge of.

In this tutorial instead of starting from scratch we will start with the
application written using only `avalanche.core`.
From that we will refactor the code using Avalanche specific features to
satisfy some reusability use-cases and to improve the tests.
It is widely recognized the correlation that testable code leads to well
modularized and reusable code, so one goal leads to the other.



Setup
=========

If you want to run the application locally first download the `AppEngine SDK <http://code.google.com/appengine/downloads.html>`_ 1.6.3 or later. Create a virtualenv as described `here <http://schettino72.wordpress.com/2010/11/21/appengine-virtualenv/>`_. (but you should use python2.7)


Add the avalanche package to your project folder.
`(pypi) <http://pypi.python.org/pypi/avalanche>`_

The complete code for this application and all steps can be found on avalanche `repository <https://bitbucket.org/schettino72/avalanche>`_ in the folder `avalanche/doc/tutorial/tasks`.


Step 0
========

On this step the code is using just avalanche.core,
not using the "real" Avalanche yet.

app.yaml
----------

This is the configuration file used by AppEngine.

`app.yaml`

.. literalinclude:: tutorial/tasks/app.yaml



tasks.py
----------

This single file contains all application code.


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

``TaskRequestHandler`` will be used as base class for all the handlers in the Task application. It is a subclass from ``core.RequestHandler``.

In this application we will use Jinja2, so we added a jinja environment to the
class to be used by all instances and a `render` method.

Apart from that it just add some string messages that will be used by the
 application.


.. code-block:: python

  import jinja2

  from avalanche.core import RequestHandler

  class TaskRequestHandler(BaseHandler):

      MSG_TASK_NEW = 'New task successfully added'
      MSG_TASK_NAME = 'Please enter a name for the task'
      MSG_TASK_CLOSED = 'Task was successfully closed'

      JINJA_ENV = jinja2.Environment(
          loader=jinja2.FileSystemLoader('templates'),
          undefined=jinja2.DebugUndefined,
          autoescape=True,
          )

      def render(self, template, **context):
          """Renders a template and writes the result to the response."""
          template = self.JINJA_ENV.get_template(template)
          uri_for = self.app.router.build # add uri_for to template
          self.response.write(template.render(uri_for=uri_for, **context))



ListTasks
+++++++++++

This handler will display the initial page with a list of tasks.
It has an option to display all tasks or just the ones that are not completed.

.. code-block:: python

  class ListTasks(TaskRequestHandler):
      """list all open tasks"""
      def get(self):
          show_closed = bool(self.request.GET.get('closed'))
          if show_closed:
              tasks = Task.all().order('created')
          else:
              tasks = Task.all().filter('closed = ', False).order('created')
          flash = self.request.GET.get('flash')
          self.render('task_list.html', tasks=tasks, flash=flash,
                      show_closed=show_closed)


NewTask
+++++++++

This handler will display a form to create a new task.
The ``post`` method creates a new Task instance and saves it into the datastore.
It also adds a message into the URL to be flashed out on the next page view.

.. code-block:: python

  class NewTask(TaskRequestHandler):
      """add a new task"""
      def get(self):
          flash = self.request.GET.get('flash')
          self.render('task_new.html', flash=flash)

      def post(self):
          name = self.request.POST.get('task-name')
          if name:
              Task(name=name).put()
              self.redirect_to('task-list', flash=self.MSG_TASK_NEW)
          else:
              self.redirect_to('task-new', flash=self.MSG_TASK_NAME)



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
          self.redirect_to('task-list', flash=self.MSG_TASK_CLOSED)



WSGI App
++++++++++++++++

Create a WSGI application mapping URI's to handlers and adding some config values.
This should really be in a different file but we will keep eveything in one module
to make it easier to follow the tutorial...

.. code-block:: python

  from avalanche.router import Route
  from avalanche.core import WSGIApplication

  def tasks_app():
      routes = [
          Route('/', ListTasks, name='task-list'),
          Route('/new', NewTask, name='task-new'),
          Route('/close/<task_id>', CloseTask, name='task-close'),
          ]
      return WSGIApplication(routes, debug=True)

  app = tasks_app()


Complete source for step 0 `tasks_0.py <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_0.py>`_



templates
----------

Create a folder name `templates` and the three Jinja template files.
We won't go through the templates in this tutorial.

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

   Re-use a request handler method using a different renderer

The goal is to make it possible to re-use the same handler method
logic but using a different template system or a different template.

The problem of the original code is that the handler method 'get' will directly
render the jinja template. To solve that we change the method to just return
the "context" used by the template and let the framework glue things together
(render the template with the given context).



avalanche.CoreHandler
-----------------------

``avalanche._AvalancheHandler`` is a `mixin <http://en.wikipedia.org/wiki/Mixin>`_
to be used with a ``core.RequestHandler``.

Actually this `avalanche._AvalancheHandler` is supposed to be used only
internally by Avalanche, we will actually remove it from the code in the next step.

So first lets make ``TaskRequestHandler`` a subclass from
`avalanche._AvalancheHandler` (and `core.RequestHandler`).

.. code-block:: diff

  + from avalanche.snow import JinjaRenderer, _AvalancheHandler
  + from avalanche.params import url_path_param

  - class TaskRequestHandler(RequestHandler):
  + class TaskRequestHandler(_AvalancheHandler, RequestHandler):

`_AvalancheHandler` provides built-in integration with jinja2 using
`JinjaRenderer`:

.. code-block:: diff

  -     JINJA_ENV = jinja2.Environment(
  -         loader=jinja2.FileSystemLoader('templates'),
  -         undefined=jinja2.DebugUndefined,
  -         autoescape=True,
  -         )
  -
  -     def render(self, template, **context):
  -         """Renders a template and writes the result to the response."""
  -         template = self.JINJA_ENV.get_template(template)
  -         uri_for = self.app.router.build # add uri_for to template
  -         self.response.write(template.render(uri_for=uri_for, **context))
  +     renderer = JinjaRenderer(jinja2.Environment(
  +             loader=jinja2.FileSystemLoader('templates'),
  +             undefined=jinja2.DebugUndefined,
  +             autoescape=True,
  +             ))



If you run the code you wont notice any difference!
The _AvalancheHandler provides a different style/abstraction to code your handlers.
But you are not strictly required to follow it.


The main role of `avalanche._AvalancheHandler` is to divide the work done
by the `get/post` handler methods into different stages.
By default ``_AvalancheHandler.get`` will call the method ``a_get`` that
is supposed to return a dictionary with the context data to be used by
the renderer. And than write renderer output into the response.

Since ``ListTasks`` also defines a ``get`` method the ``CoreHandler.get`` is
not being used...


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
            show_closed = self.request.GET.get('closed')
            if show_closed:
                tasks = Task.all().order('created')
            else:
                tasks = Task.all().filter('closed = ', False).order('created')
            flash = self.request.GET.get('flash')
  -         self.render('task_list.html', tasks=tasks, flash=flash,
  -                      show_closed=show_closed)
  +         return {'tasks': tasks,
  +                 'flash': flash,
  +                 'show_closed': show_closed,
  +                }


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
            flash = self.request.GET.get('flash')
  -         self.render('task_new.html', flash=flash)
  +         return {flash=flash}


  -     def post(self):
  +     def a_post(self):
            name = self.request.get('task-name')
            if name:
                Task(name=name).put()
                self.redirect_to('task-list', flash=self.MSG_TASK_NEW)
            else:
                self.redirect_to('task-new', flash=self.MSG_TASK_NAME)


    class CloseTask(TaskRequestHandler):
        """mark a task as closed"""
  -     def post(self, task_id):
  +     @url_path_param('task_id')
  +     def a_post(self, task_id):
            task = Task.get_by_id(int(task_id))
            task.closed = True
            task.put()
            self.redirect_to('task-list', flash=self.MSG_TASK_CLOSED)

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
  + import urllib


  + from webob import Request

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


The tests now will use the request handlers directly.
So we need to manually create and setup the handlers
(this is usually done by the app during the dispatch process).
Here is a helper function for that.

.. code-block:: diff

    + def create_handler(app, handler_class, path='', POST=None, **req_kwargs):
    +     """helper to setup request handler instances"""
    +     request = Request.blank(path, POST=POST, **req_kwargs)
    +     return handler_class(app, request)


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
    +         handler = create_handler(app, ListTasks, '?flash=flash message')
    +         ctx = handler.a_get()
    +         tasks = list(ctx['tasks'])
    +         assert len(tasks) == 2 # closed task is not included
    +         assert tasks[0].name == "my first task"
    +         assert tasks[1].name == "task 3"
    +         assert ctx['flash'] == 'flash message'
    +         assert ctx['show_closed'] == False


Note that we are not testing the template anymore. And that's exactly what we want!

The most important thing is that we are not checking for strings in HTML text
anymore. We are asserting direct values from variables.




Testing for `NewTask` post. Since the handler contains a response object we can assert the HTTP-redirect was correct:

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
  +         location = urlparse(handler.response.location)
  +         assert location.path == handler.uri_for('task-list')

            # flash message in page
  -         assert TaskRequestHandler.MSG_TASK_NEW in response
  +         query = "flash=" + urllib.quote_plus(TaskRequestHandler.MSG_TASK_NEW)
  +         assert location.query == query



You can check the other changes from the complete source of `tests step 1 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_1.py>`_



Step 2
========

.. topic:: Reusability use-case 2

   Re-use a request handler in a different application (different RequestHandler)


Our application handlers (``ListTasks``) are sub-classes
from ``core.RequestHandler``.
This makes it easy to write code because we get access to
all RequestHandler features. But the problem is that different applications
might different RequestHandler's.
So to make it reusable there should be an intermediate class so that the
application handlers do not directly subclass from ``core.RequestHandler``.

The application handlers still need to subclass from ``avalanche.BaseHandler``.
This ``BaseHandler`` is important for the configuration system
(the configuration system will be explained later).

We could create a separate handler class like this:

.. code-block:: diff

  - class TaskRequestHandler(_AvalancheHandler, RequestHandler):
  + class TaskRequestHandler(BaseHandler):

    class ListTasks(TaskRequestHandler):

  + class ListTasksHandler(ListTasks, RequestHandler, _AvalancheHandler):
  +     pass


       routes = [
  -       webapp2.Route('/', ListTasks, name='task-list'),
  +       webapp2.Route('/', ListTasksHandler, name='task-list'),


Now it easier to reuse the handler in a different application.

But creating an intermediate class for every handler would be very annoying.
Luckily in python it is very easy to create new types/classes dynamically.


.. code-block:: diff


  - class ListTasksHandler(ListTasks, RequestHandler, _AvalancheHandler):
  -     pass
  + ListTasksHandler = type('ListTasksHandler', (ListTasks, RequestHandler, _AvalancheHandler), {})

Avalanche comes with a function to that for you, ``make_handler``.
Putting all together:


.. code-block:: diff

  - from avalanche.snow import JinjaRenderer, _AvalancheRenderer
  + from avalanche.snow import make_handler, JinjaRenderer, BaseHandler

  - class TaskRequestHandler(_AvalancheHandler, RequestHandler):
  + class TaskRequestHandler(BaseHandler):

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
  +       handler_class = make_handler(RequestHandler, handler)
  +       routes.append(Route(path, handler_class, name))


Note that the user is responsible to ensure that
the RequestHandler being used has all features required by the application handler.


Complete source of `tasks.py step 2 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_2.py>`_


step 2 - tests
----------------

The tests are not modified. We just need to adjust how the handlers are created.

.. code-block:: diff

  +  from avalanche.core import RequestHandler
  +  from avalanche.snow import make_handler

     def create_handler(app, handler_class, path='', POST=None, **req_kwargs):
         """helper to setup request handler instances"""
         request = Request.blank(path, POST=POST, **req_kwargs)
  +      handler_class = make_handler(RequestHandler, handler_class)
         return handler_class(app, request)


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

  +     context_get = ['a_get', 'ctx_flash',]
  +
  +     def ctx_flash(self):
  +         flash = self.request.GET.get('flash')
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
  +   def test_ctx_flash(self, app):
  +       handler = create_handler(app, ListTasks, '?flash=flash message')
  +       ctx = handler.ctx_flash()
  +       assert ctx['flash'] == 'flash message'


    class TestListTasks(object):
        def test_get_display_not_closed(self, app):
            Task(name='my first task').put()
            Task(name='task 2', closed=True).put()
            Task(name='task 3').put()

  -         handler = create_handler(app, ListTasks, '?flash=flash message')
  +         handler = create_handler(app, ListTasks)
            ctx = handler.a_get()
            tasks = list(ctx['tasks'])
            assert len(tasks) == 2 # closed task is not included
            assert tasks[0].name == "my first task"
            assert tasks[1].name == "task 3"
  -         assert ctx['flash'] == 'flash message'
            assert ctx['show_closed'] == False

        def test_get_display_all(self, app):
            Task(name='my first task').put()
            Task(name='task 2', closed=True).put()
            Task(name='task 3').put()

  -         handler = create_handler(app, ListTasks, '?closed=1&flash=flash message')
  +         handler = create_handler(app, ListTasks, '?closed=1')
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
  -         handler = create_handler(app, NewTask, '?flash=flash message')
  -         ctx = handler.a_get()
  -         assert ctx['flash'] == 'flash message'
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

  + class FlashMixinHanlder(BaseHandler):
  +     def ctx_flash(self):
  +         flash = self.request.GET.get('flash')
  +         return {'flash': flash}

  - class TaskRequestHandler(BaseHandler):
  + class TaskRequestHandler(FlashMixinHandler, BaseHandler):

        context_get = ['a_get', 'ctx_flash',]

  -     def ctx_flash(self):
  -         flash = self.request.GET.get('flash')
  -         return {'flash': flash}

Complete source of `tasks.py step 4 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_4.py>`_

step 4 - tests
----------------

No real advantage from the point of view of tests.

.. code-block:: diff

  + from tasks import FlashMixinHandler

  - class TestTaskRequestHandler(object):
  + class TestFlashMixinHandler(object):
  -     handler = create_handler(app, ListTasks, '?flash=flash message')
  +     handler = create_handler(app, FlashMixinHandler, '?flash=flash message')
        ctx = handler.ctx_flash()
        assert ctx['flash'] == 'flash message'

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

  - from avalanche.params import url_path_param
  + from avalanche.params import url_path_param, url_query_param, post_group_param

    class FlashMixinHandler(BaseHandler):
  -     def ctx_flash(self):
  -         flash = self.request.GET.get('flash')
  +     @url_query_param('flash')
  +     def ctx_flash(self, flash):
            return {'flash': flash}


.. code-block:: diff

    class ListTasks(TaskRequestHandler):
        """list all open tasks"""
        template = 'task_list.html'

   -    def a_get(self):
   -        show_closed = bool(self.request.get('closed'))
   +    @url_query_param('show_closed', 'closed', bool)
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
  -         name = self.request.POST.get('task-name')
  +    @post_group_param('data', 'task')
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

  -    @url_path_param('task_id')
  -    def a_post(self, task_id):
  -         task = Task.get_by_id(int(task_id))
  +     @url_path_param('task', 'task_id', Task.id2task)
  +     def a_post(self, task):
            task.closed = True
            task.put()


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

    class TestFlahsHandler(object):
        def test_ctx_flash(self, app):
  -         handler = create_handler(app, FlashMixinHandler, '?flash=flash message')
  -         ctx = handler.ctx_flash()
  +         handler = create_handler(app, FlashMixinHandler)
  +         ctx = handler.ctx_flash(flash='flash message')
            assert ctx['flash'] == 'flash message'


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
  +     post_data = {'task-name':'task test xxx'}
  -     handler = create_handler(app, NewTask, POST=post_data)
  +     handler = create_handler(app, NewTask)
  -     handler.a_post()
  +     handler.a_post(data=post_data)

        # task is saved in DB
        saved = Task.all().get()

.. code-block:: diff

    def test_post_error(self, app):
  -     post_data = {'wrong-name': 'task test xxx'}
  +     post_data = {'wrong_name': 'task test xxx'}
  -     handler = create_handler(app, NewTask, POST=post_data)
  +     handler = create_handler(app, NewTask)
  -     handler.a_post()
  +     handler.a_post(data=post_data)

        # task is not saved in DB
        saved = Task.all().get()


.. code-block:: diff

   class TestCloseTask(object):
       def test_post(self, app):
           task_before = Task(name="task abc")
           task_before.put()
           assert not task_before.closed

           handler = create_handler(app, CloseTask)
  -        handler.a_post(str(task_before.key().id())
  +        handler.a_post(task_before)

           # task is closed
           task_after = Task.get_by_id(task_before.key().id())

Complete source of `tests step 5 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_5.py>`_


step 6
========

This final step will not introduce any new use-case.

The tests for HTTP 'redirect' look like quite cumbersome. ``avalanche.BaseHandler``
has a method ``a_redirect``. This method can be used instead of
``core.RequestHandler.redirect_to``, it will save the redirect info into the
attribute ``redirect_info``.


``context_param`` is used to take a value from the context.


.. code-block:: diff

     class NewTask(TaskRequestHandler):

         @post_group_param('data', 'task')
         def a_post(self, data):
             name = data.get('name')
             if name:
                 Task(name=name).put()
  -              self.redirect_to('task-list', flash=self.MSG_TASK_NEW)
  +              self.a_redirect('task-list', flash=self.MSG_TASK_NEW)
             else:
  -              self.redirect_to('task-new', flash=self.MSG_TASK_NAME)
  +              self.a_redirect('task-new', flash=self.MSG_TASK_NAME)


.. code-block:: diff

    class CloseTask(TaskRequestHandler):
        """mark a task as closed"""

        @url_path_param('task', 'task_id', Task.id2task)
        def a_post(self, task):
            task.closed = True
            task.put()
   -        self.redirect_to('task-list', flash=self.MSG_TASK_CLOSED)
   +        self.a_redirect('task-list', flash=self.MSG_TASK_CLOSED)



Complete source of `tasks.py step 6 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks_6.py>`_


step 6 - tests
----------------

So now we can test the values straight away without dealing with
conversions and quoting of values.

.. code-block:: diff

    def test_post_save(self, app):
        (...)

        # page is redirected to list page
  -     assert handler.response.status_int == 302
  -     location = urlparse(handler.response.location)
  -     assert location.path == handler.uri_for('task-list')
  -     # flash message in page
  -     query = "flash=" + urllib.quote_plus(TaskRequestHandler.MSG_TASK_NEW)
  -     assert location.query == query

  +     assert 'task-list' == handler.redirect_info[0]
  +     assert {'flash':TaskRequestHandler.MSG_TASK_NEW} == handler.redirect_info[1]


You can check the other changes from the complete source of `tests step 6 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_6.py>`_


step 7
==========

.. topic:: Reusability use-case 6

   Re-use "application" code in another web-framework

There is actually no changes required in our code to achieve that!

If you look closely the final application code for the handlers,
it makes no direct reference to webob's Request & Response objects
nor to ``avalanche.core.RequestHandler``.

In general frameworks (as opposed to libraries) should do not be used directly
in your application code.
You should just follow some conventions (or defined interfaces) and the
framework will glue all the parts together.

Lets take a closer look in the Avalanche components used in the final code.

``renderer``. Any object that has a ``render`` method would be ok.
For convencince Avalanche supplies to renderers ``JinjaRenderer`` and ``JsonRenderer``.

``param`` converter docorators. This decorators actually do not modify the
decorated methods, they will only add some "config" information to about how
to get its input values.
So your method can be used outside of the framework.

``BaseHandler``. This is required because the way the configuration system works.
And also because of the `a_redirect` method.


Complete source of final code `tasks.py <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tasks.py>`_


step 7 - tests
----------------

We can take advantage that the handlers code do not use the ``core.RequestHandler``
and remove the helper function ``create_handler`` altogether.
There is also no need to have a reference to ``tasks_app``, the handlers code
are completely independent from the application thay belong to.

A ``funcarg`` app is still required to run the tests that use the datastore.

.. code-block:: diff

    # create test app
    def pytest_funcarg__app(request):
        def create():
            my_testbed = testbed.Testbed()
            my_testbed.activate()
            my_testbed.init_datastore_v3_stub()

 -          app = tasks_app()
 -          app.testbed = my_testbed
 -          return app
 +          return my_testbed

 -      def deactivate(app):
 +      def deactivate(my_testbed):
 -          app.testbed.deactivate()
 +          my_testbed.deactivate()

        return request.cached_setup(
            setup=create,
            teardown=deactivate,
            scope="function")


.. code-block:: diff

  - from webob import Request
  - from avalanche.core import RequestHandler
  - from avalanche.snow import make_handler

  - from tasks import tasks_app, Task, TaskRequestHandler
  + from tasks import Task, TaskRequestHandler

  - def create_handler(app, handler_class, path='', POST=None, **req_kwargs):
  -     """helper to setup request handler instances"""
  -     request = Request.blank(path, POST=POST, **req_kwargs)
  -     handler_class = make_handler(RequestHandler, handler_class)
  -     return handler_class(app, request)


    class TestFlahsHandler(object):
        def test_ctx_flash(self, app):
  -         handler = create_handler(app, FlashMixinHandler)
  +         handler = FlashMixinHandler()
            ctx = handler.ctx_flash(flash='flash message')
            assert ctx['flash'] == 'flash message'



You can check the other changes from the complete source of `tests step 7 <https://bitbucket.org/schettino72/avalanche/src/tip/doc/tutorial/tasks/tests/test_tasks_7.py>`_


Other use cases
=================

Up to now Avalanche focus on getting re-usability of single
RequestHandler's separetely.
Next releases will focus on re-usability of several handlers at once.
