from google.appengine.ext import db
import jinja2

from avalanche.core import RequestHandler
from avalanche.router import Route
from avalanche.core import WSGIApplication
from avalanche.snow import JinjaRenderer, _AvalancheHandler
from avalanche.params import url_path_param

############ Models

class Task(db.Model):
    name = db.StringProperty(required=True)
    closed = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)


############ Request Handlers

class TaskRequestHandler(_AvalancheHandler, RequestHandler):

    MSG_TASK_NEW = 'New task successfully added'
    MSG_TASK_NAME = 'Please enter a name for the task'
    MSG_TASK_CLOSED = 'Task was successfully closed'

    renderer = JinjaRenderer(jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            undefined=jinja2.DebugUndefined,
            autoescape=True,
            ))



class ListTasks(TaskRequestHandler):
    """list all open tasks"""
    template = 'task_list.html'

    def a_get(self):
        show_closed = bool(self.request.GET.get('closed'))
        if show_closed:
            tasks = Task.all().order('created')
        else:
            tasks = Task.all().filter('closed = ', False).order('created')
        flash = self.request.GET.get('flash')
        return {'tasks': tasks,
                'flash': flash,
                'show_closed': show_closed,
                }


class NewTask(TaskRequestHandler):
    """add a new task"""
    template = 'task_new.html'

    def a_get(self):
        flash = self.request.GET.get('flash')
        return {'flash': flash}

    def a_post(self):
        name = self.request.POST.get('task-name')
        if name:
            Task(name=name).put()
            self.redirect_to('task-list', flash=self.MSG_TASK_NEW)
        else:
            self.redirect_to('task-new', flash=self.MSG_TASK_NAME)


class CloseTask(TaskRequestHandler):
    """mark a task as closed"""

    @url_path_param('task_id')
    def a_post(self, task_id):
        task = Task.get_by_id(int(task_id))
        task.closed = True
        task.put()
        self.redirect_to('task-list', flash=self.MSG_TASK_CLOSED)


########### WSGI App

def tasks_app():
    routes = [
        Route('/', ListTasks, name='task-list'),
        Route('/new', NewTask, name='task-new'),
        Route('/close/<task_id>', CloseTask, name='task-close'),
        ]
    return WSGIApplication(routes, debug=True)

app = tasks_app()
