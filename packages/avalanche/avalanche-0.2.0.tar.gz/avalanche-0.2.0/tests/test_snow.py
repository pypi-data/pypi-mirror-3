from urlparse import urlparse

import jinja2

from avalanche.router import Route
from avalanche.core import Request, RequestHandler, WSGIApplication
from avalanche.params import url_query_param, UrlQueryParam, UrlPathParam
from avalanche.snow import _Mixer, make_handler
from avalanche.snow import AvalancheException, ConfigurableMetaclass
from avalanche.snow import _AvalancheHandler, BaseHandler
from avalanche.snow import use_namespace, JsonRenderer, JinjaRenderer



class Test_Mixer(object):
    def test_mix(self):
        class A(object):
            x = 'a'
        class B(object):
            x = 'b'
            y = 7
        mixed = _Mixer('Mixed', (A,B), {'y':8})
        assert mixed.__name__ == 'Mixed'
        assert mixed.__class__ == type
        assert issubclass(mixed, A)
        assert issubclass(mixed, B)
        assert mixed.x == 'a'
        assert mixed.y == 8


class Test_MakeHandler(object):
    def test_make(self):
        class MyApp(BaseHandler):
            x = 1
        concrete = make_handler(RequestHandler, MyApp)
        assert concrete.__name__ == 'MyAppHandler'
        assert concrete.__class__ == ConfigurableMetaclass
        assert issubclass(concrete, RequestHandler)
        assert issubclass(concrete, _AvalancheHandler)
        assert concrete.x == 1



##### handler


class Test_BaseHandler(object):
    def test_a_config_dict_is_added_to_class(self):
        class MyHandler(BaseHandler):
            pass
        assert MyHandler.a_config == {}

    def test_a_config_get_values_from_methods(self):
        class MyHandler(BaseHandler):
            @url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']

    def test_a_config_get_values_from_subclass(self):
        class MyHandlerBase(BaseHandler):
            @url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        class MyHandler(MyHandlerBase):pass
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']
        assert MyHandler.a_config['builder_a']['x'].str_name == 'x'

    def test_a_config_modified_by_subclass(self):
        class MyHandlerBase(BaseHandler):
            @url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        class MyHandler(MyHandlerBase):
            @classmethod
            def set_config(cls):
                cls.a_config['builder_a']['x'] = UrlQueryParam('x', 'x2')
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']
        assert MyHandler.a_config['builder_a']['x'].str_name == 'x2'
        # base handler is not modified
        assert MyHandlerBase.a_config['builder_a']['x'].str_name == 'x'

    def test_a_config_subclass_of_modified(self):
        class MyHandlerBase(BaseHandler):
            @url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        class MyHandlerBase2(MyHandlerBase):
            @classmethod
            def set_config(cls):
                cls.a_config['builder_a']['x'] = UrlQueryParam('x', 'x2')
        class MyHandler(MyHandlerBase2):pass
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']
        assert MyHandler.a_config['builder_a']['x'].str_name == 'x2'


class Test_AvalancheHandler_convert_params(object):
    def test_normal(self):
        a_params = [UrlQueryParam('n_out', 'n_in', int),
                    UrlQueryParam('x2'),
                    ]
        request = Request.blank('/?n_in=5&o=other_value')
        params = _AvalancheHandler()._convert_params(request, a_params)
        assert 2 == len(params)
        assert 5 == params['n_out']
        assert '' == params['x2']

    def test_unused_param(self):
        a_params = [UrlPathParam('n')]
        request = Request.blank('/')
        request.route_kwargs = {}
        params = _AvalancheHandler()._convert_params(request, a_params)
        assert 0 == len(params)


class Test_AvalancheHandler_builder(object):

    def test_ok(self):
        class MyHandler(_AvalancheHandler):
            def my_builder(self): # pragma: nocover
                pass
        handler = MyHandler()
        assert handler.my_builder == handler._builder('my_builder')

    def test_invalid_list_context_builder(self):
        class MyHandler(_AvalancheHandler):
            pass
        handler = MyHandler()
        try:
            handler._builder('a_get')
        except Exception, error:
            assert 'MyHandler' in str(error)
            assert 'a_get' in str(error)
        else: # pragma: nocover
            assert False, 'didnt raise exception'

    def test_invalid_list_context_builder_type(self):
        class MyHandler(_AvalancheHandler):
            pass
        handler = MyHandler()
        try:
            handler._builder(345)
        except AvalancheException, error:
            assert 'wrong type' in str(error)
            assert 'string' in str(error)
            assert 'MyHandler' in str(error)
            assert '345' in str(error)
        else: # pragma: nocover
            assert False, 'didnt raise exception'


class Test_AvalancheHandler_build_context(object):
    def test_no_param(self):
        class MyHandler(_AvalancheHandler):
            def a_get(self):
                return {'x': None}
        handler = MyHandler()
        request = Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {'x': None} == handler.context

    def test_error_no_param(self):
        class MyHandler(_AvalancheHandler):
            def a_get(self, number): # pragma: nocover
                pass

        handler = MyHandler()
        request = Request.blank('/?n=12')
        try:
            handler._build_context(handler.context_get, request)
        except AvalancheException, error:
            assert 'a_get' in str(error)
        else: # pragma: nocover
            assert False, 'didnt raise exception'


    def test_builder_specific_param(self):
        class MyHandler(_AvalancheHandler):
            @url_query_param('number', 'n', int)
            def a_get(self, number):
                return {'x': number}
        handler = MyHandler()
        request = Request.blank('/?n=12')
        handler._build_context(handler.context_get, request)
        assert {'x':12} == handler.context


    def test_context_raises_exception(self):
        class MyHandler(_AvalancheHandler):
            def a_get(self):
                raise TypeError('user code')

        handler = MyHandler()
        request = Request.blank('/')
        try:
            handler._build_context(handler.context_get, request)
        except TypeError, error:
            assert 'user code' == str(error)
        else: # pragma: nocover
            assert False, 'didnt raise exception'

    def test_context_namespace(self):
        class MyHandler(_AvalancheHandler):
            context_get = ['xxx']
            @use_namespace
            def xxx(self):
                return {'a':'A'}
        handler = MyHandler()
        request = Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {'xxx':{'a':'A'}} == handler.context


    def test_context_built_is_None(self):
        class MyHandler(_AvalancheHandler):
            def a_get(self):
                pass
        handler = MyHandler()
        request = Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {} == handler.context

    def test_context_built_is_None_with_namespace(self):
        class MyHandler(_AvalancheHandler):
            def a_get(self):
                return None
            a_get.use_namespace = True
        handler = MyHandler()
        request = Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {'a_get':None} == handler.context



###################################################


class _AppHandler(BaseHandler):
    renderer = JinjaRenderer(jinja2.Environment(
            loader=jinja2.FileSystemLoader('tests/templates'),
            undefined=jinja2.DebugUndefined,
            autoescape=True,
            ))

AppHandler = make_handler(RequestHandler, _AppHandler)

base_app = WSGIApplication([Route('/', BaseHandler, 'index')])



class Test_AppHandler_get(object):
    def test_get_render_jinja(self):
        class MyHandler(AppHandler):
            template = "sample_jinja.html"
            def a_get(self):
                return {'x': 33}
        handler = MyHandler(base_app, Request.blank('/'))
        handler.dispatch()
        assert 'X is 33' == handler.response.body

    def test_render_shortcut(self):
        class MyHandler(AppHandler):
            template = "sample_jinja.html"
        handler = MyHandler(base_app, Request.blank('/'))
        handler.render(x=33)
        assert 'X is 33' == handler.response.body


    def test_get_no_render(self):
        # no template
        class MyHandler(AppHandler):
            def a_get(self):
                pass
        request = Request.blank('/')
        handler = MyHandler(base_app, request)
        handler.get()
        assert '' == handler.response.body

    def test_get_render_json(self):
        class MyHandler(AppHandler):
            renderer = JsonRenderer()
            def a_get(self):
                return {'x': 33}
        request = Request.blank('/')
        handler = MyHandler(base_app, request)
        handler.get()
        assert '{"x": 33}' == handler.response.body

    def test_redirect(self):
        class MyHandler(AppHandler):
            def a_get(self):
                self.a_redirect('index', par1='one')
        request = Request.blank('/')
        handler = MyHandler(base_app, request)
        handler.get()
        assert handler.response.status_int == 302
        assert urlparse(handler.response.location).path == handler.uri_for('index')



class Test_AppHandler_post(object):
    def test_post(self):
        called = [] # modifies this
        class MyHandler(AppHandler):
            def a_post(self):
                called.append(True)
        request = Request.blank('/')
        handler = MyHandler(base_app, request)
        handler.post()
        assert [True] == called

    def test_redirect(self):
        class MyHandler(AppHandler):
            def a_post(self):
                self.a_redirect('index', par1='one')
        request = Request.blank('/')
        handler = MyHandler(base_app, request)
        handler.post()
        assert handler.response.status_int == 302
        assert urlparse(handler.response.location).path == handler.uri_for('index')


