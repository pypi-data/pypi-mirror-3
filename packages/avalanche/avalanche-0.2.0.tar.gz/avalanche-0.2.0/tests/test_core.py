import pytest

from webob import exc

from avalanche.router import Route
from avalanche.core import Request
from avalanche.core import RequestHandler, WSGIApplication


class TestRequestHandler(object):

    def test_normalize_handler_method(self):
        assert "x_y" == RequestHandler._normalize_handler_method('x-y')


class TestRequestHandler_Dispatch(object):

    # test method not allowed
    def test_405(self):
        # supports only post method
        class OnlyPost(RequestHandler):
            def post(self): # pragma: nocover
                pass

        app = WSGIApplication(())
        handler = OnlyPost(app, Request.blank('/'))
        try:
            handler.dispatch()
        except exc.HTTPMethodNotAllowed as exception:
            # must list allowed methods
            assert ('POST',) == exception.allow
        else: # pragma: nocover
            assert False


    def test_dispatch_writes_on_default_response(self):
        class Sample(RequestHandler):
            def get(self):
                self.response.write('hello')

        app = WSGIApplication(())
        handler = Sample(app, Request.blank('/'))
        handler.dispatch()
        assert 'hello' == handler.response.body


    def test_dispatch_with_params(self):
        class Sample(RequestHandler):
            def get(self, *args, **kwargs):
                return args, kwargs

        app = WSGIApplication(())
        handler = Sample(app, Request.blank('/'))
        handler.dispatch(1, 2, a='xyz')
        assert (1,2) == handler.response[0]
        assert {'a':'xyz'} == handler.response[1]


    def test_handle_exception_dafault(self):
        # it actually re-raise last exception
        class Sample(RequestHandler):
            pass
        handler = Sample(None, None)
        try:
            raise Exception('default handler')
        except Exception:
            try:
                handler.handle_exception(None)
            except Exception as exception:
                assert 'default handler' in str(exception)
            else: # pragma: nocover
                assert False


    def test_handle_exception_custom(self):
        class Sample(RequestHandler):
            def get(self):
                raise Exception('xxx')

            def handle_exception(self, exception):
                return 'handled ok'

        app = WSGIApplication(())
        handler = Sample(app, Request.blank('/'))
        handler.dispatch()
        assert 'handled ok' == handler.response



class TestRequestHandler_Redirect(object):

    def pytest_funcarg__handler(self, request):
        class Sample(RequestHandler):pass
        app = WSGIApplication(())
        return Sample(app, Request.blank('/one/two/three'))


    def test_absolute_url(self, handler):
        handler.redirect('/3b')
        assert 'http://localhost/3b' == handler.response.location

    def test_relative_url(self, handler):
        handler.redirect('3b')
        assert '3b' == handler.response.location

    def test_relative_url_2(self, handler):
        handler.redirect('../3b')
        assert 'http://localhost/one/3b' == handler.response.location

    def test_body_cleared(self, handler):
        handler.response.write('trash')
        handler.redirect('/')
        assert '' == handler.response.body

    def test_body_arg(self, handler):
        handler.response.write('trash')
        handler.redirect('/', body='moo')
        assert 'moo' == handler.response.body


    def test_code_default_302(self, handler):
        handler.redirect('/')
        assert 302 == handler.response.status_int

    def test_code_permanent_301(self, handler):
        handler.redirect('/', permanent=True)
        assert 301 == handler.response.status_int

    def test_code_custom(self, handler):
        handler.redirect('/', code=307)
        assert 307 == handler.response.status_int

    def test_code_invalid(self, handler):
        pytest.raises(AssertionError, handler.redirect, '/', code=400)

    def test_redirect_to(self):
        routes = [Route('/here', None, 'index')]
        app = WSGIApplication(routes)
        class Sample(RequestHandler):pass
        handler = Sample(app, Request.blank('/one/two/three'))

        assert '/here' == handler.uri_for('index')
        handler.redirect_to('index', _code=303)
        assert 'http://localhost/here' == handler.response.location
        assert 303 == handler.response.status_int



class TestWSGIApplication(object):

    def test_http_not_implemented(self):
        app = WSGIApplication([Route('/', RequestHandler)])
        environ = {'REQUEST_METHOD': 'XXX'}
        response = Request.blank('/', environ=environ).get_response(app)
        assert 501 == response.status_int

    def test_404(self):
        app = WSGIApplication([Route('/', RequestHandler)])
        response = Request.blank('/worng-path').get_response(app)
        assert 404 == response.status_int

    def test_ok(self):
        class Sample(RequestHandler):
            def get(self):
                self.response.write('hello test ok')
        app = WSGIApplication([Route('/', Sample)])
        response = Request.blank('/').get_response(app)
        assert 'hello test ok' == response.body

    def test_internal_error(self):
        class Sample(RequestHandler):
            def get(self):
                raise Exception('i fail')
        app = WSGIApplication([Route('/', Sample)])
        response = Request.blank('/').get_response(app)
        assert 500 == response.status_int
        assert 'Internal Server Error' in response.body

    def test_internal_error_html(self):
        class Sample(RequestHandler):
            def get(self):
                raise Exception('i fail')
        app = WSGIApplication([Route('/', Sample)], debug=True)
        response = Request.blank('/').get_response(app)
        assert 500 == response.status_int
        assert 'i fail' in response.body

    def test_invalid_response(self):
        class Sample(RequestHandler):
            def get(self):
                return 'xxx'
        app = WSGIApplication([Route('/', Sample)])
        response = Request.blank('/').get_response(app)
        assert 500 == response.status_int
        assert 'Internal Server Error' in response.body

    def test_handle_exception(self):
        class Handle404(RequestHandler):
            def get(self, exception):
                self.response.write('not here')
        app = WSGIApplication(error_handlers={404:Handle404})
        response = Request.blank('/').get_response(app)
        assert 404 == response.status_int
        assert 'not here' == response.body

