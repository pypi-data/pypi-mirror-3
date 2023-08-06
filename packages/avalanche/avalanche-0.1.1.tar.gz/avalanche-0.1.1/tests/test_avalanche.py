import webapp2
#import pytest

import avalanche


class TestHandler(avalanche.CoreHandler, webapp2.RequestHandler):
    _config = {}
    _config['webapp2_extras.jinja2'] = {'template_path':'tests/templates'}
    app = webapp2.WSGIApplication(config=_config)



class Test_AddListItemDecorator(object):
    def test_first_item(self):
        @avalanche.AddListItemDecorator('list_x', "X33")
        def sample(xxx): #pragma: nocover
            pass
        assert 1 == len(sample.list_x)
        assert "X33" == sample.list_x[0]

    def test_two_items(self):
        @avalanche.AddListItemDecorator('xs', "X1")
        @avalanche.AddListItemDecorator('xs', "X2")
        def sample(xxx): #pragma: nocover
            pass
        assert 2 == len(sample.xs)
        assert "X2" == sample.xs[0]
        assert "X1" == sample.xs[1]


class Test_Mixer(object):
    def test_mix(self):
        class A(object):
            x = 'a'
        class B(object):
            x = 'b'
            y = 7
        mixed = avalanche._Mixer('Mixed', (A,B), {'y':8})
        assert mixed.__name__ == 'Mixed'
        assert mixed.__class__ == type
        assert issubclass(mixed, A)
        assert issubclass(mixed, B)
        assert mixed.x == 'a'
        assert mixed.y == 8


class Test_MakeHandler(object):
    def test_make(self):
        class MyApp(avalanche.AvalancheHandler):
            x = 1
        concrete = avalanche.make_handler(webapp2.RequestHandler, MyApp)
        assert concrete.__name__ == 'MyAppHandler'
        assert concrete.__class__ == avalanche.ConfigurableMetaclass
        assert issubclass(concrete, webapp2.RequestHandler)
        assert issubclass(concrete, avalanche.CoreHandler)
        assert concrete.x == 1


class Test_AvalanchParam(object):
    def test_init(self):
        aparam = avalanche.AvalancheParam('n1', 'n2')
        assert 'n1' == aparam.obj_name
        assert 'n2' == aparam.str_name

    def test_init_no_obj_name(self):
        aparam = avalanche.AvalancheParam('n')
        assert 'n' == aparam.obj_name
        assert 'n' == aparam.str_name

    def test_get_obj_value(self):
        aparam = avalanche.AvalancheParam('n1', 'n2', int)
        assert 2 == aparam.get_obj_value('2', None)

    def test_get_obj_value_no_conversion(self):
        aparam = avalanche.AvalancheParam('n1', 'n2')
        assert '2' == aparam.get_obj_value('2', None)

    def test_get_obj_value_use_handler(self):
        fake_handler = 'fake handler'
        def my_converter(xxx, handler):
            return "%s-%s" % (handler, xxx)
        aparam = avalanche.AvalancheParam('n1', 'n2', my_converter)
        assert 'fake handler-2' == aparam.get_obj_value('2', fake_handler)

    def test_get_obj_value_no_use_handler(self):
        fake_handler = 'fake handler'
        def my_converter(xxx, yyy='no'):
            return "%s-%s" % (yyy, xxx)
        aparam = avalanche.AvalancheParam('n1', 'n2', my_converter)
        assert 'no-2' == aparam.get_obj_value('2', fake_handler)

    def test_repr(self):
        aparam = avalanche.AvalancheParam('n1', 'n2')
        assert repr(aparam) == '<AvalancheParam:n1-n2>'


class Test_UrlPathParam(object):
    def test_get_str_value(self):
        aparam = avalanche.UrlPathParam('n')
        request = webapp2.Request.blank('/')
        request.route_kwargs = {'n': 'n_value', 'o': 'other_value',}
        assert 'n_value' == aparam.get_str_value(request)

    def test_decorator(self):
        aparam = avalanche.url_path_param('x')
        assert isinstance(aparam, avalanche.AddListItemDecorator)
        assert isinstance(aparam.item, avalanche.UrlPathParam)
        assert avalanche._PARAM_VAR == aparam.list_var


class Test_UrlQueryParam(object):
    def test_get_str_value(self):
        aparam = avalanche.UrlQueryParam('n')
        request = webapp2.Request.blank('/?n=n_value&o=other_value')
        assert 'n_value' == aparam.get_str_value(request)

    def test_decorator(self):
        aparam = avalanche.url_query_param('x')
        assert isinstance(aparam, avalanche.AddListItemDecorator)
        assert isinstance(aparam.item, avalanche.UrlQueryParam)
        assert avalanche._PARAM_VAR == aparam.list_var


class Test_PostGroupParam(object):
    def test_get_value(self):
        aparam = avalanche.PostGroupParam('xy')
        request = webapp2.Request.blank('/?xy-a=1&xy-bb=23&other=other_value')
        handler = webapp2.RequestHandler(request)
        data = aparam.get_obj_value(aparam.get_str_value(request), handler)
        assert 2 == len(data)
        assert '1' == data['a']
        assert '23' == data['bb']

    def test_decorator(self):
        aparam = avalanche.post_group_param('xy', 'xdata')
        assert isinstance(aparam, avalanche.AddListItemDecorator)
        assert isinstance(aparam.item, avalanche.PostGroupParam)
        assert avalanche._PARAM_VAR == aparam.list_var



class Test_ContextParam(object):

    def test_get_value(self):
        aparam = avalanche.ContextParam('this_user', 'user')
        request = webapp2.Request.blank('/')
        handler = avalanche.CoreHandler()
        handler.context = {'user': 'babu'}
        data = aparam.get_obj_value(aparam.get_str_value(request), handler)
        assert 'babu' == data

    def test_decorator(self):
        aparam = avalanche.context_param('this_user', 'user')
        assert isinstance(aparam, avalanche.AddListItemDecorator)
        assert isinstance(aparam.item, avalanche.ContextParam)
        assert avalanche._PARAM_VAR == aparam.list_var


##### handler


class Test_AvalancheHandler(object):
    def test_a_config_dict_is_added_to_class(self):
        class MyHandler(avalanche.AvalancheHandler):
            pass
        assert MyHandler.a_config == {}

    def test_a_config_get_values_from_methods(self):
        class MyHandler(avalanche.AvalancheHandler):
            @avalanche.url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']

    def test_a_config_get_values_from_subclass(self):
        class MyHandlerBase(avalanche.AvalancheHandler):
            @avalanche.url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        class MyHandler(MyHandlerBase):pass
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']
        assert MyHandler.a_config['builder_a']['x'].str_name == 'x'

    def test_a_config_modified_by_subclass(self):
        class MyHandlerBase(avalanche.AvalancheHandler):
            @avalanche.url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        class MyHandler(MyHandlerBase):
            @classmethod
            def set_config(cls):
                cls.a_config['builder_a']['x'] = avalanche.UrlQueryParam('x', 'x2')
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']
        assert MyHandler.a_config['builder_a']['x'].str_name == 'x2'
        # base handler is not modified
        assert MyHandlerBase.a_config['builder_a']['x'].str_name == 'x'

    def test_a_config_subclass_of_modified(self):
        class MyHandlerBase(avalanche.AvalancheHandler):
            @avalanche.url_query_param('x')
            def builder_a(self, x): #pragma: no cover
                pass
        class MyHandlerBase2(MyHandlerBase):
            @classmethod
            def set_config(cls):
                cls.a_config['builder_a']['x'] = avalanche.UrlQueryParam('x', 'x2')
        class MyHandler(MyHandlerBase2):pass
        assert 'builder_a' in MyHandler.a_config
        assert 'x' in MyHandler.a_config['builder_a']
        assert MyHandler.a_config['builder_a']['x'].str_name == 'x2'


class Test_CoreHandler_convert_params(object):
    def test_normal(self):
        a_params = [avalanche.UrlQueryParam('n_out', 'n_in', int),
                    avalanche.UrlQueryParam('x2'),
                    ]
        request = webapp2.Request.blank('/?n_in=5&o=other_value')
        params = avalanche.CoreHandler()._convert_params(request, a_params)
        assert 2 == len(params)
        assert 5 == params['n_out']
        assert '' == params['x2']

    def test_unused_param(self):
        a_params = [avalanche.UrlPathParam('n')]
        request = webapp2.Request.blank('/')
        request.route_kwargs = {}
        params = avalanche.CoreHandler()._convert_params(request, a_params)
        assert 0 == len(params)


class Test_CoreHandler_builder(object):

    def test_ok(self):
        class MyHandler(avalanche.CoreHandler):
            def my_builder(self): # pragma: nocover
                pass
        handler = MyHandler()
        assert handler.my_builder == handler._builder('my_builder')

    def test_invalid_list_context_builder(self):
        class MyHandler(avalanche.CoreHandler):
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
        class MyHandler(avalanche.CoreHandler):
            pass
        handler = MyHandler()
        try:
            handler._builder(345)
        except avalanche.AvalancheException, error:
            assert 'wrong type' in str(error)
            assert 'string' in str(error)
            assert 'MyHandler' in str(error)
            assert '345' in str(error)
        else: # pragma: nocover
            assert False, 'didnt raise exception'


class Test_CoreHandler_build_context(object):
    def test_no_param(self):
        class MyHandler(avalanche.CoreHandler):
            def a_get(self):
                return {'x': None}
        handler = MyHandler()
        request = webapp2.Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {'x': None} == handler.context

    def test_error_no_param(self):
        class MyHandler(avalanche.CoreHandler):
            def a_get(self, number): # pragma: nocover
                pass

        handler = MyHandler()
        request = webapp2.Request.blank('/?n=12')
        try:
            handler._build_context(handler.context_get, request)
        except avalanche.AvalancheException, error:
            assert 'a_get' in str(error)
        else: # pragma: nocover
            assert False, 'didnt raise exception'


    def test_builder_specific_param(self):
        class MyHandler(avalanche.CoreHandler):
            @avalanche.url_query_param('number', 'n', int)
            def a_get(self, number):
                return {'x': number}
        handler = MyHandler()
        request = webapp2.Request.blank('/?n=12')
        handler._build_context(handler.context_get, request)
        assert {'x':12} == handler.context


    def test_context_raises_exception(self):
        class MyHandler(avalanche.CoreHandler):
            def a_get(self):
                raise TypeError('user code')

        handler = MyHandler()
        request = webapp2.Request.blank('/')
        try:
            handler._build_context(handler.context_get, request)
        except TypeError, error:
            assert 'user code' == str(error)
        else: # pragma: nocover
            assert False, 'didnt raise exception'

    def test_context_namespace(self):
        class MyHandler(avalanche.CoreHandler):
            context_get = ['xxx']
            @avalanche.use_namespace
            def xxx(self):
                return {'a':'A'}
        handler = MyHandler()
        request = webapp2.Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {'xxx':{'a':'A'}} == handler.context


    def test_context_built_is_None(self):
        class MyHandler(avalanche.CoreHandler):
            def a_get(self):
                pass
        handler = MyHandler()
        request = webapp2.Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {} == handler.context

    def test_context_built_is_None_with_namespace(self):
        class MyHandler(avalanche.CoreHandler):
            def a_get(self):
                return None
            a_get.use_namespace = True
        handler = MyHandler()
        request = webapp2.Request.blank('/')
        handler._build_context(handler.context_get, request)
        assert {'a_get':None} == handler.context


class Test_CoreHandler_get(object):
    def test_get_render_jinja(self):
        class MyHandler(TestHandler):
            template = "sample_jinja.html"
            def a_get(self):
                return {'x': 33}
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = MyHandler(request, response)
        handler.get()
        assert 'X is 33' == response.body

    def test_render_shortcut(self):
        class MyHandler(TestHandler):
            template = "sample_jinja.html"
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = MyHandler(request, response)
        handler.render({'x': 33})
        assert 'X is 33' == response.body


    def test_get_no_render(self):
        # no template
        class MyHandler(avalanche.CoreHandler, webapp2.RequestHandler):
            def a_get(self):
                pass
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = MyHandler(request, response)
        handler.get()
        assert '' == response.body

    def test_get_render_json(self):
        class MyHandler(TestHandler):
            renderer = avalanche.JsonRenderer()
            def a_get(self):
                return {'x': 33}
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = MyHandler(request, response)
        handler.get()
        assert '{"x":33}' == response.body



class Test_CoreHandler_post(object):
    def test_post(self):
        called = [] # modifies this
        class MyHandler(TestHandler):
            def a_post(self):
                called.append(True)
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = MyHandler(request, response)
        handler.post()
        assert [True] == called

