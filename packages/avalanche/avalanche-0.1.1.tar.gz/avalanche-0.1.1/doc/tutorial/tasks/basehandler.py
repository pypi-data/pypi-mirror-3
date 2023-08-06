import logging
import traceback
import sys
import cgi

import webapp2
from webapp2_extras import sessions, jinja2


class BaseHandler(webapp2.RequestHandler):
    """handler with jinja2 renderer and sessions enabled"""

    ######## session ######################
    def _make_session_store(self):
        self.session_store = sessions.get_store(request=self.request)

    def dispatch(self):
        # Get a session store for this request.
        self._make_session_store()

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
    ######## end - session #################


    ######## jinja2 ########################
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        """Renders a template and writes the result to the response."""
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)
    ######## end jinja2 ####################


    #### copied from webapp.RequestHandler.handle_exception
    def handle_exception(self, exception, debug_mode):
        """Called if this handler throws an exception during execution.

        The default behavior is to call self.error(500) and print a stack trace
        if debug_mode is True.

        Args:
          exception: the exception that was thrown
          debug_mode: True if the web application is running in debug mode
        """
        self.error(500)
        logging.exception(exception)
        if debug_mode:
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            self.response.clear()
            self.response.out.write('<pre>%s</pre>' % (cgi.escape(lines, quote=True)))
