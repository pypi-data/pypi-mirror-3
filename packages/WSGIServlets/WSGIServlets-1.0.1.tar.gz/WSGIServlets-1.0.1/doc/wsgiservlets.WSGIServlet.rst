wsgiservlets.WSGIServlet
========================

.. currentmodule:: wsgiservlets


Instances of WSGIServlet are WSGI applications (by implementing
the method :meth:`__call__()` following the WSGI protocol...see
`PEP 3333 <http://www.python.org/dev/peps/pep-3333>`_).

To create a new subclass of WSGIServlet you must implement,
minimally, :meth:`_lifecycle`.  If you want to serve HTML you
probably don't want to subclass WSGIServlet, but rather subclass
:class:`HTMLPage`, which already subclasses WSGIServlet and has
many features for generating HTML output.  The complete list of
subclasses of WSGIServlet in the standard distribution:

    * :class:`HTMLPage`: generates well-formed HTML documents and
      has many methods and attributes to make generating web pages
      easy.
      
    * :class:`Dispatcher`: given a mapping of names to WSGIServlet
      classes and optionally a document root, subclasses of
      ``Dispatcher`` can serve (dispatch) a mix of static and
      dynamic content.

    * :class:`JSONRPCServer`: a JSON-RPC service.  Subclasses that
      define methods with names prefixed *rpc_* are automatically
      available to remote clients.  These methods can except any
      arguments and return any object(s) that can be json
      encoded/decoded.


API:

.. autoclass:: WSGIServlet
   :members:
   :member-order: bysource

   .. automethod:: __call__
   .. automethod:: _pre_lifecycle
   .. automethod:: _lifecycle
   .. automethod:: _post_lifecycle
