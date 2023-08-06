""" Avalanche - Web Framework with a focus on testability and reusability

"""

__version__ = "0.1.1"


import inspect
import copy

import webapp2
from webapp2_extras import jinja2, json


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



# FIXME - make this configurable
def use_namespace(func):
    """decorator that add use_namespace=True to function"""
    func.use_namespace = True
    return func


class AvalancheException(Exception):
    pass


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
        return request.get(self.str_name)


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
            for arg in request.arguments():
                if arg.startswith(prefix):
                    name = arg[prefix_len:]
                    data[name] = request.get(arg)
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



############ render

class JinjaRenderer(object):
    @staticmethod
    def render(handler, context):
        """Renders a template and writes the result to the response."""
        if handler.template:
            rv = handler.jinja2.render_template(handler.template, **context)
            handler.response.write(rv)


class JsonRenderer(object):
    @staticmethod
    def render(handler, context):
        handler.response.write(json.encode(context))



########## handler

# name of the variable added to context_builders to hold
# list of AvalancheParam
_PARAM_VAR = '_a_params'


class ConfigurableMetaclass(type):
    """adds an attribute (dict) 'a_config' to the class

    * when the class is created it merges the confing from base classes
    * collect config info from the class methods
    * calls classmethod set_config (used by subclasses to alter config values
      from base classes)
    """
    def __new__(mcs, name, bases, dict_):
        # create class
        _class = type.__new__(mcs, name, bases, dict_)

        config = {}

        # get config from base classes
        for base_class in bases:
            if hasattr(base_class, 'a_config'):
                config.update(copy.deepcopy(base_class.a_config))

        # get config values from builders decorators
        for attr_name in dict_.iterkeys():
            # get a_param from method
            attr = getattr(_class, attr_name)
            a_params = getattr(attr, _PARAM_VAR, None)
            if not a_params:
                continue
            # add to config dict
            handler_config = config.setdefault(attr_name, {})
            for param in a_params:
                handler_config[param.obj_name] = param
        _class.a_config = config

        # modify config
        _class.set_config()
        return _class



class CoreHandler(object):
    """Core avalanche functionality.

    Users should not subclass this directly, use :py:func:`avalanche.make_handler`.
    """

    # @ivar context: (dict) with values computed on context_builders

    # TODO: support context_builders defined in a different class
    # this would allow make_handler combine many AvalancheHandler's without
    # subclassing them.

    __metaclass__ = ConfigurableMetaclass

    @classmethod
    def set_config(cls):pass

    #: list of context-builder method names used on GET requests
    context_get = ['a_get', ]

    #: list of context-builder method names used on POST requests
    context_post = ['a_post', ]

    # use Jinja renderer by default
    renderer = JinjaRenderer()

    #: (string) path to jinja template to be rendered
    template = None


    def _convert_params(self, request, param_list):
        """convert params from HTTP string to python objects

         @param param_list: list of AvalancheParam
         @return dict
        """
        param_objs = {}
        for param in param_list:
            str_value = param.get_str_value(request)
            if str_value is not None:
                obj_value = param.get_obj_value(str_value, self)
                param_objs[param.obj_name] = obj_value
        return param_objs


    def _builder(self, name):
        """retrieve builder method, give precise error messages if fails"""
        try:
            return getattr(self, name)
        except TypeError:
            msg_str = ("Error on handler '%s' context builder list contains " +
                   "an item with wrong type. " +
                   "List must contain strings with method names, " +
                   "got (%s: %r).")
            msg = msg_str % (self.__class__.__name__, type(name), name)
            raise AvalancheException(msg)


    def _build_context(self, builders, request):
        """build context for given builders
        @param builders: list of string of builder method names
        """

        # build context
        self.context = {}
        for builder_name in builders:
            builder = self._builder(builder_name)
            # get builder specific obj_params
            if builder_name in self.a_config:
                a_params = self.a_config[builder_name].values()
                param_objs = self._convert_params(request, a_params)
            else:
                param_objs = {}

            # run builder
            try:
                built_context = builder(**param_objs)
            except TypeError, exception:
                if 'arguments' not in str(exception):
                    # should catch only:
                    # TypeEror:"xxx takes exactly X arguments (Y given))"
                    raise
                msg_str = ("Error on handler incomplete parameters for " +
                       "builder '%s.%s'. Got params %r, (Original error:%s)")
                msg = msg_str % (self.__class__.__name__, builder.__name__,
                                 param_objs, str(exception))
                raise AvalancheException(msg)

            # update handler context
            if getattr(builder, 'use_namespace', False):
                # use namespace
                self.context[builder_name] = built_context
            else:
                if built_context is not None:
                    self.context.update(built_context)


    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)


    def render(self, context):
        self.renderer.render(self, context)

    def get(self, *args, **kwargs):
        """
          * build context
          * render template
        """
        self._build_context(self.context_get, self.request)
        self.render(self.context)

    def post(self, *args, **kwargs):
        """build_context should redirect page"""
        self._build_context(self.context_post, self.request)



class AvalancheHandler(object):
    """Base class that user should subclass when creating request handlers"""

    __metaclass__ = ConfigurableMetaclass
    @classmethod
    def set_config(cls):
        """used to modify config values inherited from a base class

        config values are saved as a dict in the attribute 'a_config'.

         * on first level keys are the name of config-builders
         * on second level keys are the parameter names
         * values are instances of AvalancheParam

        ::

          class MyHandler(MyHandlerBase):
              @classmethod
              def set_config(cls):
                  cls.a_config['builder_a']['x'] = avalanche.UrlQueryParam('x', 'x2')
        """
        pass



def _Mixer(class_name, bases, dict_=None):
    """create a new class/type with given name and base classes"""
    return type(class_name, bases, dict_ or {})


def make_handler(webapp2_handler, app_handler, dict_=None):
    """creates a concrete request handler
     => ApplicationHandler(AvalancheHandler) + CoreHandler +
     webapp2.RequestHandler
    """
    handler_name = app_handler.__name__ + 'Handler'
    bases = (app_handler, CoreHandler, webapp2_handler)
    return _Mixer(handler_name, bases, dict_)
