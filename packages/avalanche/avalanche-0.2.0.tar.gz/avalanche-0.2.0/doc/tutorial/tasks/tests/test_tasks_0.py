import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from webtest import TestApp
from google.appengine.ext import testbed

from tasks_0 import tasks_app, Task, TaskRequestHandler

# create test app
def pytest_funcarg__app(request):
    def create():
        my_testbed = testbed.Testbed()
        my_testbed.activate()
        my_testbed.init_datastore_v3_stub()

        app = TestApp(tasks_app())
        app.testbed = my_testbed
        return app

    def deactivate(app):
        app.testbed.deactivate()

    return request.cached_setup(
        setup=create,
        teardown=deactivate,
        scope="function")


###############################################

class TestListTasks(object):
    def test_get_display_not_closed(self, app):
        Task(name='my first task').put()
        Task(name='task 2', closed=True).put()
        Task(name='task 3').put()
        response = app.get('/')
        assert "Task's List" in response
        assert "show closed" in response
        assert "my first task" in response
        assert "task 2" not in response
        assert "task 3" in response

    def test_get_display_all(self, app):
        Task(name='my first task').put()
        Task(name='task 2', closed=True).put()
        Task(name='task 3').put()
        response = app.get('/?closed=1')
        assert "Task's List" in response
        assert "hide closed" in response
        assert "my first task" in response
        assert "task 2" in response
        assert "task 3" in response


class TestNewTask(object):
    def test_get(self, app):
        response = app.get('/new')
        assert "Add a new task" in response

    def test_post_save(self, app):
        response_0 = app.post('/new', {'task-name':'task test xxx'})

        # task is saved in DB
        saved = Task.all().get()
        assert saved
        assert 'task test xxx' == saved.name

        # page is redirected to list page
        response = response_0.follow()
        assert "Task's List" in response

        # flash message in page
        assert TaskRequestHandler.MSG_TASK_NEW in response


    def test_post_error(self, app):
        response_0 = app.post('/new', {'wrong-name':'task test xxx'})

        # task is not saved in DB
        saved = Task.all().get()
        assert not saved

        # page is redirected to list page
        response = response_0.follow()
        assert "Add a new task" in response

        # flash message in page
        assert TaskRequestHandler.MSG_TASK_NAME in response


class TestCloseTask(object):
    def test_post(self, app):
        task_before = Task(name="task abc")
        task_before.put()
        assert not task_before.closed

        response_0 = app.post('/close/%s' % task_before.key().id())

        # task is closed
        task_after = Task.get_by_id(task_before.key().id())
        assert task_after.closed

        # page is redirected to list page
        response = response_0.follow()
        assert "Task's List" in response

        # flash message in page
        assert TaskRequestHandler.MSG_TASK_CLOSED in response
