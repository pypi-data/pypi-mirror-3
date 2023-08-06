from google.appengine.ext import db

import webapp2

from basehandler import BaseHandler


############ Models

class Task(db.Model):
    name = db.StringProperty(required=True)
    closed = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)


############ Request Handlers

class TaskRequestHandler(BaseHandler):

    MSG_TASK_NEW = 'New task successfully added'
    MSG_TASK_NAME = 'Please enter a name for the task'
    MSG_TASK_CLOSED = 'Task was successfully closed'



class ListTasks(TaskRequestHandler):
    """list all open tasks"""
    def get(self):
        show_closed = bool(self.request.get('closed'))
        if show_closed:
            tasks = Task.all().order('created')
        else:
            tasks = Task.all().filter('closed = ', False).order('created')
        flash = self.session.get_flashes()
        self.render_response('task_list.html', tasks=tasks, flash=flash,
                             show_closed=show_closed)


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


class CloseTask(TaskRequestHandler):
    """mark a task as closed"""
    def post(self, task_id):
        task = Task.get_by_id(int(task_id))
        task.closed = True
        task.put()
        self.session.add_flash(self.MSG_TASK_CLOSED)
        self.redirect(self.uri_for('task-list'))


########### WSGI App

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
