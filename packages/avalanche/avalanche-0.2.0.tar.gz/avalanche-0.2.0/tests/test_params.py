
from avalanche.core import Request, RequestHandler
from avalanche.params import AddListItemDecorator, AvalancheParam, _PARAM_VAR
from avalanche.params import UrlPathParam, url_path_param
from avalanche.params import UrlQueryParam, url_query_param
from avalanche.params import PostGroupParam, post_group_param
from avalanche.params import ContextParam, context_param
from avalanche.snow import _AvalancheHandler


class Test_AddListItemDecorator(object):
    def test_first_item(self):
        @AddListItemDecorator('list_x', "X33")
        def sample(xxx): #pragma: nocover
            pass
        assert 1 == len(sample.list_x)
        assert "X33" == sample.list_x[0]

    def test_two_items(self):
        @AddListItemDecorator('xs', "X1")
        @AddListItemDecorator('xs', "X2")
        def sample(xxx): #pragma: nocover
            pass
        assert 2 == len(sample.xs)
        assert "X2" == sample.xs[0]
        assert "X1" == sample.xs[1]


class Test_AvalanchParam(object):
    def test_init(self):
        aparam = AvalancheParam('n1', 'n2')
        assert 'n1' == aparam.obj_name
        assert 'n2' == aparam.str_name

    def test_init_no_obj_name(self):
        aparam = AvalancheParam('n')
        assert 'n' == aparam.obj_name
        assert 'n' == aparam.str_name

    def test_get_obj_value(self):
        aparam = AvalancheParam('n1', 'n2', int)
        assert 2 == aparam.get_obj_value('2', None)

    def test_get_obj_value_no_conversion(self):
        aparam = AvalancheParam('n1', 'n2')
        assert '2' == aparam.get_obj_value('2', None)

    def test_get_obj_value_use_handler(self):
        fake_handler = 'fake handler'
        def my_converter(xxx, handler):
            return "%s-%s" % (handler, xxx)
        aparam = AvalancheParam('n1', 'n2', my_converter)
        assert 'fake handler-2' == aparam.get_obj_value('2', fake_handler)

    def test_get_obj_value_no_use_handler(self):
        fake_handler = 'fake handler'
        def my_converter(xxx, yyy='no'):
            return "%s-%s" % (yyy, xxx)
        aparam = AvalancheParam('n1', 'n2', my_converter)
        assert 'no-2' == aparam.get_obj_value('2', fake_handler)

    def test_repr(self):
        aparam = AvalancheParam('n1', 'n2')
        assert repr(aparam) == '<AvalancheParam:n1-n2>'


class Test_UrlPathParam(object):
    def test_get_str_value(self):
        aparam = UrlPathParam('n')
        request = Request.blank('/')
        request.route_kwargs = {'n': 'n_value', 'o': 'other_value',}
        assert 'n_value' == aparam.get_str_value(request)

    def test_decorator(self):
        aparam = url_path_param('x')
        assert isinstance(aparam, AddListItemDecorator)
        assert isinstance(aparam.item, UrlPathParam)
        assert _PARAM_VAR == aparam.list_var


class Test_UrlQueryParam(object):
    def test_get_str_value(self):
        aparam = UrlQueryParam('n')
        request = Request.blank('/?n=n_value&o=other_value')
        assert 'n_value' == aparam.get_str_value(request)

    def test_decorator(self):
        aparam = url_query_param('x')
        assert isinstance(aparam, AddListItemDecorator)
        assert isinstance(aparam.item, UrlQueryParam)
        assert _PARAM_VAR == aparam.list_var


class Test_PostGroupParam(object):
    def test_get_value(self):
        aparam = PostGroupParam('xy')
        post_data = {'xy-a':1,'xy-bb':23, 'other':'other_value'}
        request = Request.blank('/', POST=post_data)
        handler = RequestHandler(None, request)
        data = aparam.get_obj_value(aparam.get_str_value(request), handler)
        assert 2 == len(data)
        assert '1' == data['a']
        assert '23' == data['bb']

    def test_decorator(self):
        aparam = post_group_param('xy', 'xdata')
        assert isinstance(aparam, AddListItemDecorator)
        assert isinstance(aparam.item, PostGroupParam)
        assert _PARAM_VAR == aparam.list_var



class Test_ContextParam(object):

    def test_get_value(self):
        aparam = ContextParam('this_user', 'user')
        request = Request.blank('/')
        handler = _AvalancheHandler()
        handler.context = {'user': 'babu'}
        data = aparam.get_obj_value(aparam.get_str_value(request), handler)
        assert 'babu' == data

    def test_decorator(self):
        aparam = context_param('this_user', 'user')
        assert isinstance(aparam, AddListItemDecorator)
        assert isinstance(aparam.item, ContextParam)
        assert _PARAM_VAR == aparam.list_var

