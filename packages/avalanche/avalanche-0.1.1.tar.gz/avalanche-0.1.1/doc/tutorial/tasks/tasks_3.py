from google.appengine.ext import db

import webapp2
import avalanche

from basehandler import BaseHandler


############ Models

class Task(db.Model):
    name = db.StringProperty(required=True)
    closed = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)


############ Request Handlers

class TaskRequestHandler(avalanche.AvalancheHandler):

    MSG_TASK_NEW = 'New task successfully added'
    MSG_TASK_NAME = 'Please enter a name for the task'
    MSG_TASK_CLOSED = 'Task was successfully closed'

    context_get = ['a_get', 'ctx_flash',]

    def ctx_flash(self):
        flash = self.session.get_flashes()
        return {'flash': flash}




class ListTasks(TaskRequestHandler):
    """list all open tasks"""
    template = 'task_list.html'

    def a_get(self):
        show_closed = bool(self.request.get('closed'))
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

    def a_post(self):
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

    @avalanche.url_path_param('task_id')
    def a_post(self, task_id):
        task = Task.get_by_id(int(task_id))
        task.closed = True
        task.put()
        self.session.add_flash(self.MSG_TASK_CLOSED)
        self.redirect(self.uri_for('task-list'))


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
