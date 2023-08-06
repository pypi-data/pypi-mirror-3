import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from urlparse import urlparse
import urllib

from google.appengine.ext import testbed
from webob import Request

from tasks_1 import tasks_app, Task, TaskRequestHandler
from tasks_1 import ListTasks, NewTask, CloseTask

# create test app
def pytest_funcarg__app(request):
    def create():
        my_testbed = testbed.Testbed()
        my_testbed.activate()
        my_testbed.init_datastore_v3_stub()

        app = tasks_app()
        app.testbed = my_testbed
        return app

    def deactivate(app):
        app.testbed.deactivate()

    return request.cached_setup(
        setup=create,
        teardown=deactivate,
        scope="function")


def create_handler(app, handler_class, path='', POST=None, **req_kwargs):
    """helper to setup request handler instances"""
    request = Request.blank(path, POST=POST, **req_kwargs)
    return handler_class(app, request)


###############################################

class TestListTasks(object):
    def test_get_display_not_closed(self, app):
        Task(name='my first task').put()
        Task(name='task 2', closed=True).put()
        Task(name='task 3').put()

        handler = create_handler(app, ListTasks, '?flash=flash message')
        ctx = handler.a_get()
        tasks = list(ctx['tasks'])
        assert len(tasks) == 2 # closed task is not included
        assert tasks[0].name == "my first task"
        assert tasks[1].name == "task 3"
        assert ctx['flash'] == 'flash message'
        assert ctx['show_closed'] == False

    def test_get_display_all(self, app):
        Task(name='my first task').put()
        Task(name='task 2', closed=True).put()
        Task(name='task 3').put()

        handler = create_handler(app, ListTasks, '?closed=1&flash=flash message')
        ctx = handler.a_get()
        tasks = list(ctx['tasks'])
        assert len(tasks) == 3
        assert tasks[0].name == "my first task"
        assert tasks[1].name == "task 2"
        assert tasks[2].name == "task 3"
        assert ctx['flash'] == 'flash message'
        assert ctx['show_closed'] == True


class TestNewTask(object):
    def test_get(self, app):
        handler = create_handler(app, NewTask, '?flash=flash message')
        ctx = handler.a_get()
        assert ctx['flash'] == 'flash message'

    def test_post_save(self, app):
        post_data = {'task-name':'task test xxx'}
        handler = create_handler(app, NewTask, POST=post_data)
        handler.a_post()

        # task is saved in DB
        saved = Task.all().get()
        assert saved
        assert 'task test xxx' == saved.name

        # page is redirected to list page
        assert handler.response.status_int == 302
        location = urlparse(handler.response.location)
        assert location.path == handler.uri_for('task-list')
        # flash message in page
        query = "flash=" + urllib.quote_plus(TaskRequestHandler.MSG_TASK_NEW)
        assert location.query == query


    def test_post_error(self, app):
        post_data = {'wrong-name': 'task test xxx'}
        handler = create_handler(app, NewTask, POST=post_data)
        handler.a_post()

        # task is not saved in DB
        saved = Task.all().get()
        assert not saved

        # page is redirected to list page
        assert handler.response.status_int == 302
        location = urlparse(handler.response.location)
        assert location.path == handler.uri_for('task-new')
        # flash message in page
        query = "flash=" + urllib.quote_plus(TaskRequestHandler.MSG_TASK_NAME)
        assert location.query == query


class TestCloseTask(object):
    def test_post(self, app):
        task_before = Task(name="task abc")
        task_before.put()
        assert not task_before.closed

        handler = create_handler(app, CloseTask, POST={})
        handler.a_post(str(task_before.key().id()))

        # task is closed
        task_after = Task.get_by_id(task_before.key().id())
        assert task_after.closed

        # page is redirected to list page
        assert handler.response.status_int == 302
        location = urlparse(handler.response.location)
        assert location.path == handler.uri_for('task-list')

        # flash message in page
        query = "flash=" + urllib.quote_plus(TaskRequestHandler.MSG_TASK_CLOSED)
        assert location.query == query
