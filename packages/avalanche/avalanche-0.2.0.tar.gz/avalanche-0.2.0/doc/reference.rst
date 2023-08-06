==============
API Reference
==============

Request & Response
=====================

check `webob docs <http://docs.webob.org>`_


Routing
==========

.. autoclass:: avalanche.router.Route
   :members: __init__, build, match

.. autoclass:: avalanche.router.MatchResult

.. autoclass:: avalanche.router.Router
   :members: __init__, add, build, match




core.RequestHandler
=====================

.. autoclass:: avalanche.core.RequestHandler
   :members: __init__, dispatch, redirect, uri_for, redirect_to, handle_exception

core.WSGIApplication
======================

.. autoclass:: avalanche.core.WSGIApplication
   :members: __init__, internal_error


Renderers
=============

Any object that implements that implements a `render` method.
``render`` method takes 2 parameters:

  * `handler`: a reference
  * `context`: a dictionary

Avalanche comes with to renderers:

.. autoclass:: avalanche.snow.JinjaRenderer
   :members: __init__, render

.. autoclass:: avalanche.snow.JsonRenderer
   :members: render



Avalanche Request Handlers
----------------------------

User's should create handlers by subclassing ``BaseHandler``.

``make_handler`` result should be used on the WSGIApplication.


.. autofunction:: avalanche.snow.make_handler

.. autoclass:: avalanche.snow._AvalancheHandler

   .. autoattribute:: avalanche.snow._AvalancheHandler.context_get

   .. autoattribute:: avalanche.snow._AvalancheHandler.context_post

   .. autoattribute:: avalanche.snow._AvalancheHandler.renderer

   .. autoattribute:: avalanche.snow._AvalancheHandler.template


.. autoclass:: avalanche.snow.BaseHandler

    .. automethod:: avalanche.snow.BaseHandler.set_config

    .. autoattribute:: avalanche.snow.BaseHandler.redirect_info

    .. automethod:: avalanche.snow.BaseHandler.a_redirect




Context-builder parameter converter
=======================================

.. autoclass:: avalanche.params.AvalancheParam

   .. automethod:: avalanche.params.AvalancheParam.get_str_value


.. autofunction:: avalanche.params.UrlPathParam

.. autofunction:: avalanche.params.UrlQueryParam

.. autofunction:: avalanche.params.PostGroupParam

.. autofunction:: avalanche.params.ContextParam


decorators
----------------

The following decorators are provided to config context-builders:

.. autofunction:: avalanche.params.url_path_param

.. autofunction:: avalanche.params.url_query_param

.. autofunction:: avalanche.params.post_group_param

.. autofunction:: avalanche.params.context_param
