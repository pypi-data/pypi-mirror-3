from google.appengine.ext import db
import jinja2

from avalanche.core import RequestHandler
from avalanche.router import Route
from avalanche.core import WSGIApplication
from avalanche.snow import make_handler, JinjaRenderer, BaseHandler
from avalanche.params import url_path_param, url_query_param, post_group_param


############ Models

class Task(db.Model):
    name = db.StringProperty(required=True)
    closed = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def id2task(task_id):
        """@param task_id: (str)"""
        return Task.get_by_id(int(task_id))


############ Request Handlers

class FlashMixinHandler(BaseHandler):
    @url_query_param('flash')
    def ctx_flash(self, flash):
        return {'flash': flash}


class TaskRequestHandler(FlashMixinHandler, BaseHandler):

    MSG_TASK_NEW = 'New task successfully added'
    MSG_TASK_NAME = 'Please enter a name for the task'
    MSG_TASK_CLOSED = 'Task was successfully closed'

    renderer = JinjaRenderer(jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            undefined=jinja2.DebugUndefined,
            autoescape=True,
            ))

    context_get = ['a_get', 'ctx_flash',]




class ListTasks(TaskRequestHandler):
    """list all open tasks"""
    template = 'task_list.html'

    @url_query_param('show_closed', 'closed', bool)
    def a_get(self, show_closed):
        if show_closed:
            tasks = Task.all().order('created')
        else:
            tasks = Task.all().filter('closed = ', False).order('created')
        return {'tasks': tasks,
                'show_closed': show_closed,
                }


class NewTask(TaskRequestHandler):
    """add a new task"""
    template = 'task_new.html'

    def a_get(self): # pragma: no cover
        pass

    @post_group_param('data', 'task')
    def a_post(self, data):
        name = data.get('name')
        if name:
            Task(name=name).put()
            self.redirect_to('task-list', flash=self.MSG_TASK_NEW)
        else:
            self.redirect_to('task-new', flash=self.MSG_TASK_NAME)


class CloseTask(TaskRequestHandler):
    """mark a task as closed"""

    @url_path_param('task', 'task_id', Task.id2task)
    def a_post(self, task):
        task.closed = True
        task.put()
        self.redirect_to('task-list', flash=self.MSG_TASK_CLOSED)


########### WSGI App

def tasks_app():
    route_raw = [('/', ListTasks, 'task-list'),
                 ('/new', NewTask, 'task-new'),
                 ('/close/<task_id>', CloseTask, 'task-close')
                 ]
    routes = []
    for path, handler, name in route_raw:
        handler_class = make_handler(RequestHandler, handler)
        routes.append(Route(path, handler_class, name))
    return WSGIApplication(routes, debug=True)

app = tasks_app()
