# -*- coding: utf-8 -*-

import urllib

import pytest

from webob import Request
from avalanche.router import Route, Router

req = Request.blank

class Test_Route_Repr(object):
    def test(self):
        route = Route('/xxx', None)
        assert "<Route('/xxx', None)>" == repr(route)


class Test_Route_Match(object):
    def test_no_vars(self):
        route = Route('/xxx', None)
        assert ((),{}) == route.match(req('/xxx'))
        assert None == route.match(req('/xxxx'))
        assert None == route.match(req('/2xxx'))
        assert None == route.match(req('2/xxx'))
        assert None == route.match(req('/xxx/'))

    def test_named_var(self):
        route = Route('/edit/<key>', None)
        assert ((), {'key':'123'}) == route.match(req('/edit/123'))
        assert ((), {'key':'45'}) == route.match(req('/edit/45'))
        assert None == route.match(req('/edit/123/45'))

    def test_named_var_2(self):
        route = Route('/edit-<key>', None)
        assert ((), {'key':'123'}) == route.match(req('/edit-123'))
        assert ((), {'key':'45'}) == route.match(req('/edit-45'))
        assert None == route.match(req('/edit-123/45'))

    def test_regex_var(self):
        route = Route('/edit/<key:\d{3}>', None)
        assert ((), {'key':'123'}) == route.match(req('/edit/123'))
        assert None == route.match(req('/edit/45'))

    def test_positional_var(self):
        route = Route('/edit/<>', None)
        assert (('123',), {}) == route.match(req('/edit/123'))
        assert (('45',), {}) == route.match(req('/edit/45'))
        assert None == route.match(req('/edit/xx/'))

    def test_positional_var_2(self):
        route = Route('/edit/<>/<>', None)
        assert (('123', '45'), {}) == route.match(req('/edit/123/45'))
        assert None == route.match(req('/edit/123'))

    def test_named_positional_var(self):
        route = Route('/edit/<>/<action>', None)
        assert (('123',), {'action':'go'}) == route.match(req('/edit/123/go'))

    def test_named_positional_var_2(self):
        route = Route('/edit/<action>/<>', None)
        assert (('123',), {'action':'go'}) == route.match(req('/edit/go/123'))


class Test_Route_build(object):
    def test_no_vars(self):
        route = Route('/xxx', None)
        assert '/xxx' == route.build((), {})
        # positional argument is just ignored
        assert '/xxx?d1=abc' == route.build('p1', d1='abc')

    def test_named_var(self):
        route = Route('/edit/<key>', None)
        assert '/edit/123' == route.build(key='123')

    def test_missing_var(self):
        route = Route('/edit/<key>', None)
        pytest.raises(Exception, route.build)

    def test_var_obj(self):
        route = Route('/edit/<key>', None)
        assert '/edit/123' == route.build(key=123)

    def test_var_unicode(self):
        route = Route('/', None)
        url = route.build(foo=u'olá')
        assert urllib.unquote(url).decode('utf-8') == u'/?foo=olá'

    def test_positional_var(self):
        route = Route('/edit/<>', None)
        assert '/edit/123' == route.build(123)

    def test_named_positional_var(self):
        route = Route('/edit/<>/<action>', None)
        assert '/edit/123/go' == route.build(123, action='go')

    def test_named_positional_var_2(self):
        route = Route('/edit/<action>/<>', None)
        assert '/edit/go/123' == route.build(123, action='go')

    def test_fragment(self):
        route = Route('/xxx', None)
        built = route.build(action='go', _fragment='part2')
        assert '/xxx?action=go#part2' == built

    def test_scheme_netloc(self):
        route = Route('/xxx', None)
        built = route.build(action='go', _scheme='https', _netloc='example.com')
        assert 'https://example.com/xxx?action=go' == built



class TestRouter(object):
    def test_match(self):
        r1 = Route('/', None, 'index')
        r2 = Route('/r2', None, 'page2')
        r3 = Route('/r3', None)
        router = Router(r1, r2, r3)

        assert None == router.match(req('nono'))
        assert (r2, (), {}) == router.match(req('/r2'))


    def test_build(self):
        r1 = Route('/', None, 'index')
        r2 = Route('/r2/<name>', None, 'page2')
        router = Router(r1, r2)

        assert '/r2/col?y=1961' == router.build('page2', name='col', y=1961)
        pytest.raises(Exception, router.build, 'nonono')
