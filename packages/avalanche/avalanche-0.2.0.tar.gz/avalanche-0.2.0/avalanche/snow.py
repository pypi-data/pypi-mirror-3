import copy
import json

from .params import _PARAM_VAR



class AvalancheException(Exception):
    pass


# FIXME - make this configurable - document
def use_namespace(func):
    """decorator that add use_namespace=True to function"""
    func.use_namespace = True
    return func


############ render

class JinjaRenderer(object):
    """render jinja2 templates"""
    def __init__(self, jinja_env):
        """

        :param jinja_env:
            instance of jinja2.Environment

        """
        self.jinja_env = jinja_env

    def render(self, handler, **context):
        """Renders handler.template and writes the result to its response"""
        if handler.template:
            template = self.jinja_env.get_template(handler.template)
            uri_for = handler.app.router.build
            handler.response.write(template.render(
                    uri_for=uri_for,
                    handler=handler,
                    **context))


class JsonRenderer(object):
    """render json data"""
    @staticmethod
    def render(handler, **context):
        """write response to handler's reponse """
        handler.response.write(json.dumps(context).replace("</", "<\\/"))



class ConfigurableMetaclass(type):
    """adds an attribute (dict) 'a_config' to the class

    * when the class is created it merges the confing from base classes
    * collect config info from the class methods (using _PARAM_VAR)
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



class _AvalancheHandler(object):
    """avalanche functionality.

    Users should not subclass this directly, use ``make_handler``
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

    #: tuple with (name, dict) to be passed to redirect_to
    redirect_info = ()

    #: A `renderer` instance
    renderer = None

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


    def render(self, **context):
        self.renderer.render(self, **context)


    def get(self, *args, **kwargs):
        """
          * build context
          * render template
        """
        # FIXME - do no attach stuff to request object!
        self.request.route_kwargs = kwargs
        self._build_context(self.context_get, self.request)
        if self.redirect_info:
            self.redirect_to(self.redirect_info[0], **self.redirect_info[1])
        # XXX how to specify render should not occur
        self.render(**self.context)

    def post(self, *args, **kwargs):
        """build_context should redirect page"""
        self.request.route_kwargs = kwargs
        self._build_context(self.context_post, self.request)
        if self.redirect_info:
            self.redirect_to(self.redirect_info[0], **self.redirect_info[1])



class BaseHandler(object):
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


    #: tuple with (name, dict) to be passed to redirect_to
    redirect_info = ()

    def a_redirect(self, _name, **kwargs):
        """do not redirect now just saves ``redirect_info``"""
        self.redirect_info = (_name, kwargs)




def _Mixer(class_name, bases, dict_=None):
    """create a new class/type with given name and base classes"""
    return type(class_name, bases, dict_ or {})


def make_handler(request_handler, app_handler, dict_=None):
    """creates a concrete request handler
     => ApplicationHandler(avalanche.Handler) + _AvalancheHandler +
     core.RequestHandler
    """
    handler_name = app_handler.__name__ + 'Handler'
    bases = (app_handler, request_handler, _AvalancheHandler)
    return _Mixer(handler_name, bases, dict_)

