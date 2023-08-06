from google.appengine.ext import db

import webapp2
import avalanche

from basehandler import BaseHandler


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

class FlashMixinHandler(avalanche.AvalancheHandler):
    def ctx_flash(self):
        flash = self.session.get_flashes()
        return {'flash': flash}

    @avalanche.context_param('messages', 'flash')
    def add_flash(self, messages):
        for msg in messages:
            self.session.add_flash(msg)


class TaskRequestHandler(FlashMixinHandler, avalanche.AvalancheHandler):

    MSG_TASK_NEW = 'New task successfully added'
    MSG_TASK_NAME = 'Please enter a name for the task'
    MSG_TASK_CLOSED = 'Task was successfully closed'

    context_get = ['a_get', 'ctx_flash',]
    context_post = ['a_post', 'add_flash',]


class ListTasks(TaskRequestHandler):
    """list all open tasks"""
    template = 'task_list.html'

    @avalanche.url_query_param('show_closed', 'closed', bool)
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

    @avalanche.post_group_param('data', 'task')
    def a_post(self, data):
        ctx = {'flash': []}
        name = data.get('name')
        if name:
            Task(name=name).put()
            ctx['flash'].append(self.MSG_TASK_NEW)
            self.redirect(self.uri_for('task-list'))
        else:
            ctx['flash'].append(self.MSG_TASK_NAME)
            self.redirect(self.uri_for('task-new'))
        return ctx

class CloseTask(TaskRequestHandler):
    """mark a task as closed"""

    @avalanche.url_path_param('task', 'task_id', Task.id2task)
    def a_post(self, task):
        ctx = {'flash': []}
        task.closed = True
        task.put()
        ctx['flash'].append(self.MSG_TASK_CLOSED)
        self.redirect(self.uri_for('task-list'))
        return ctx


########### WSGI App

def tasks_app():
    route_raw = [('/', ListTasks, 'task-list'),
                 ('/new', NewTask, 'task-new'),
                 ('/close/<task_id>', CloseTask, 'task-close')
                 ]
    routes = []
    for path, handler, name in route_raw:
        handler_class = avalanche.make_handler(BaseHandler, handler)
        routes.append(webapp2.Route(path, handler_class, name))
    config = {}
    config['webapp2_extras.sessions'] = {'secret_key': '1234567890'}
    config['webapp2_extras.jinja2'] = {'globals': {'uri_for': webapp2.uri_for}}

    return  webapp2.WSGIApplication(routes, debug=True, config=config)


app = tasks_app()
