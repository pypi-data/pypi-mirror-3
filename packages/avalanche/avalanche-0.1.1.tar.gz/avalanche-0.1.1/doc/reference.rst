==============
API Reference
==============

.. currentmodule:: avalanche

Request Handlers
------------------

.. autofunction:: make_handler

.. autoclass:: CoreHandler

.. autoclass:: AvalancheHandler

   .. automethod:: AvalancheHandler.set_config

   .. autoattribute:: CoreHandler.context_get

   .. autoattribute:: CoreHandler.context_post

   .. py:attribute:: CoreHandler.renderer

      A :ref:`renderer` instance. By default it is a :py:class:`avalanche.JinjaRenderer`

   .. autoattribute:: CoreHandler.template



.. _renderer:

Renderer
-----------

Any object that implements that implements a `render` method can be used as
:py:attr:`CoreHandler.renderer`. It takes 2 parameters:

 * `handler`: a reference to a :py:class:`AvalancheHandler`
 * `context`: a dictionary

Avalanche comes with to renderers

.. autoclass:: JinjaRenderer

.. autoclass:: JsonRenderer



Context-builder parameter converter
---------------------------------------

.. autoclass:: AvalancheParam

   .. automethod:: AvalancheParam.get_str_value


.. autofunction:: UrlPathParam

.. autofunction:: UrlQueryParam

.. autofunction:: PostGroupParam

.. autofunction:: ContextParam


decorators
++++++++++

The following decorators are provided to config context-builders:

.. autofunction:: url_path_param

.. autofunction:: url_query_param

.. autofunction:: post_group_param

.. autofunction:: context_param
