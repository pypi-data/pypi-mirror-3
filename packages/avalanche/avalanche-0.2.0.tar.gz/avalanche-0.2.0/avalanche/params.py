import inspect


# name of the variable added to context_builders to hold
# list of AvalancheParam
_PARAM_VAR = '_a_params'


class AddListItemDecorator(object):
    """decorator that adds an item to a list variable in the decorated function

    @return the original function

    @ivar list_var: (str) name of variable to store the list of items
    @ivar item: item to be added
    """
    def __init__(self, list_var, item):
        self.list_var = list_var
        self.item = item
    def __call__(self, func):
        if not hasattr(func, self.list_var):
            setattr(func, self.list_var, [])
        getattr(func, self.list_var).append(self.item)
        return func



class AvalancheParam(object):
    """A parameter converter - (Abstract base class)

    This is used to convert parameters (i.e. from the URL) from string to its
    real type.

    :param obj_name: name of param to be passed to context_builders
    :type obj_name: str

    :param str_name: name of param on the source
                     if not provided use same as obj_name
    :type str_name: str

    :param str2obj: callable that converts param string to an object
                    if not provided obj it just returns the str_value
                    there are 2 acceptable signatures for the callable:

                     * take a single param with the str_value
                     * first param takes str_value, second is named 'handler'
                       and receives a reference to the RequestHandler
    """

    def __init__(self, obj_name, str_name=None, str2obj=None):
        self.obj_name = obj_name
        self.str_name = str_name or obj_name
        self.str2obj = str2obj

    def get_str_value(self, request): #pragma: nocover
        """intermediate value that will be passed to str2obj"""
        raise NotImplementedError

    def get_obj_value(self, str_value, handler):
        """return object value
        @param handler: reference to a RequestHandler
        """
        if self.str2obj:
            # XXX remove this shit. if needs handler call it a 'get_obj'
            if inspect.isfunction(self.str2obj):
                args = inspect.getargspec(self.str2obj)[0]
                if len(args) > 1 and args[1] == 'handler':
                    return self.str2obj(str_value, handler)
            return self.str2obj(str_value)
        else:
            return str_value

    def __repr__(self):
        return "<%s:%s-%s>" % (self.__class__.__name__,
                              self.obj_name, self.str_name)


###### Param sources

class UrlPathParam(AvalancheParam):
    """get parameter from URL path (given by route)"""
    def get_str_value(self, request):
        return request.route_kwargs.get(self.str_name)

def url_path_param(obj_name, str_name=None, str2obj=None):
    """decorator to add a UrlPathParam to a context-builder"""
    a_param = UrlPathParam(obj_name, str_name, str2obj)
    return AddListItemDecorator(_PARAM_VAR, a_param)


class UrlQueryParam(AvalancheParam):
    """get parameter from the URL query string"""
    def get_str_value(self, request):
        #XXX no difference between not present and ''. really want this?
        return request.GET.get(self.str_name, '')


def url_query_param(obj_name, str_name=None, str2obj=None):
    """decorator to add a UrlQueryParam to a context-builder"""
    converter = UrlQueryParam(obj_name, str_name, str2obj)
    return AddListItemDecorator(_PARAM_VAR, converter)



class PostGroupParam(AvalancheParam):
    """get a dictionary with all paramaters which name starts with "<str_name>-"
    """

    def __init__(self, obj_name, str_name=None):
        def str2obj(str_value, handler):
            data = {}
            prefix = '%s-' % str_value
            prefix_len = len(prefix)
            request = handler.request
            for arg in request.POST.iterkeys():
                if arg.startswith(prefix):
                    name = arg[prefix_len:]
                    data[name] = request.POST.get(arg)
            return data

        AvalancheParam.__init__(self, obj_name, str_name, str2obj)

    def get_str_value(self, request):
        return self.str_name


def post_group_param(obj_name, str_name=None):
    """decorator to add a PostGroupParam to a context-builder"""
    converter = PostGroupParam(obj_name, str_name)
    return AddListItemDecorator(_PARAM_VAR, converter)


class ContextParam(AvalancheParam):
    """get param from request-handler context"""
    def __init__(self, obj_name, str_name=None):
        def convert(str_value, handler):
            return handler.context[str_value]

        AvalancheParam.__init__(self, obj_name, str_name)
        self.str2obj = convert

    def get_str_value(self, request):
        return self.str_name

def context_param(obj_name, str_name=None):
    converter = ContextParam(obj_name, str_name)
    return AddListItemDecorator(_PARAM_VAR, converter)


