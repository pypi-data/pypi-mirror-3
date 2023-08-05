# -*- python -*-

## Copyright 2011 Daniel J. Popowich
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import sys, os, time, base64, cgi
import Cookie
import traceback

from wsgiservlets.constants import *
from wsgiservlets.httpresponse import *
from wsgiservlets.descriptors import *
from wsgiservlets.session import *

__all__ = ['WSGIServlet']

class WSGIServlet(object):
    """Abstract base class for all servlets, instances of which are WSGI applications.
    

    """

    __metaclass__ = servletmeta

    auth_realm = 'Unspecified'
    """Specifies the realm for basic HTTP authentication.  Default:
    ``'Unspecified'``."""
    
    use_form = True
    """If ``use_form`` evaluates to ``True`` (the default) then for
    each request ``form`` will be set to an instance of
    :class:`cgi.FieldStorage`.  If ``False``, ``form`` will be
    set to ``None``."""

    form = None
    """See :attr:`use_form`."""
    
    use_session = False
    """If ``use_session`` evaluates to ``True`` then for each request
    ``session`` will be set to an instance of
    :class:`Session`.  If ``False`` (the default),
    ``session`` will be set to ``None``."""

    session = None
    """See :attr:`use_session`."""

    session_cookie_name = 'wsgisrv_sid'
    """If sessions are in use (see :attr:`use_session`), then this is
    the name of the session cookie set on the client."""
    
    @property
    def session_cookie_secret(self):
        """The client cookie holding the session ID is signed to avoid
        hijacking session IDs.  ``session_cookie_secret`` should be
        unique string to seed the digital string.

        .. note:: used by all servlets accessing the same Session
           backend

        """
        
        # Force setting this manually for security
        raise NotImplementedError, \
              'You must set `session_cookie_secret` for your servlet'

    session_config = {'timeout' : SESSION_TIMEOUT,
                      'hold_exclusive_lock' : False,}
    """A mapping holding session configuration variables.  At this
    time there are two variables:

       1. **timeout** (default: ``1800``) The amount of time, in seconds,
          before a session times out.

       2. **hold_exclusive_lock** (default: ``False``) If true, a lock
          will be held through the whole request before being
          released, thus serializing requests from the same session.
    """

    session_backend = FileSessionBackend
    """Specifies the type of session to use.  Currently, only one kind
    of session is in the distribution: :class:`FileSessionBackend`.
    """

    session_backend_init = {'cachedir' : FILESESSION_CACHEDIR}
    """Session backend configuration, which is backend specific.  For
    :class:`FileSessionBackend` the only variable is:

      1. **cachedir** (default: ``/tmp/wsgisrv_sess``) which specifies
         the root directory for session storage.
    """

    cookieclass = Cookie.SimpleCookie
    """The class to use when accessing/setting client cookies.  Any
    class can be used, but it should follow the protocol of those
    classes defined in the standard python library module
    :mod:`Cookie`.  The default is :class:`Cookie.SimpleCookie`."""
    

    method = environ_helper('REQUEST_METHOD')
    """Same as ``environ['REQUEST_METHOD']``"""

    script_name = environ_helper('SCRIPT_NAME')
    """Same as ``environ['SCRIPT_NAME']``"""

    path_info = environ_helper('PATH_INFO')
    """Same as ``environ['PATH_INFO']``"""

    query_string = environ_helper('QUERY_STRING')
    """Same as ``environ['QUERY_STRING']``"""
    
    debug = False
    """If true (default: ``False``) exceptions will send stack traces
    and a pretty-printed listing of the environment to the client.
    Other objects in :mod:`wsgiservlets` also flag debugging output
    on this variable."""
    
    gen500msg = ('Oops!  We seem to be having some technical difficulty. '
                 'Please try again later.')
    """Terse message sent to clients on status 500 responses."""

    def __init__(self):
        """Base class constructor takes no arguments and ensures it's
        not being called on the base class (an abstract base class
        which should not be instantiated) by raising a
        :exc:`RuntimeError`.  Subclasses are free to override the
        constructor.
        """
        
        if self.__class__ is WSGIServlet:
            raise RuntimeError, 'WSGIServlet is an abstract base class'

    def __str__(self):
        '''Return a simple string representing an instance'''

        return 'WSGIServlet %s' % self.__class__.__name__

    def __call__(self, environ, start_response):

        """WSGIServlet instances are WSGI applications by virtue of
        the implementation of this method which adheres to the protocol
        specified in `PEP 3333 <http://www.python.org/dev/peps/pep-3333>`_.

        :param environ: the WSGI environment.
        :param start_response: the start response callable.
        :rtype: an instance of :class:`wsgiservlets.HTTPResponse`
                which are iterable.


        The implementation is simple in principle and follows these
        steps:

           #. cache ``environ`` as :attr:`environ`
           #. create :attr:`response` as an instance of :class:`wsgiservlets.HTTPOK`
           #. call, in order:
               #. :meth:`_pre_lifecycle`                
               #. :meth:`_lifecycle`                
               #. :meth:`_post_lifecycle`
           #. return :attr:`response`
        
        """

        # stuff the environment in servlet
        self.environ = environ
        # create a response object...we assume it will be OK
        self.response = HTTPOK()
        # initialize cache
        self._db = {}
                
        try:
            try:
                self._pre_lifecycle()
                self._lifecycle()
            except HTTPResponse, response:
                pass
            except Exception, e:
                response = self._gen500(e)
            else:
                response = self.response
            finally:
                self._post_lifecycle()

            if environ.get('wsgiservlets.subrequest'):
                raise response

        finally:
            self.environ = self.response = self._db = None
        
        return response(start_response)

    environ = None
    '''The WSGI environment.'''
    
    response = None
    '''The response object, an instance of :class:`HTTPResponse`.'''
    
    def _pre_lifecycle(self):
        '''See :meth:`__call__` for when this method is called in the life
        cycle of a request.  The base class implementation initializes
        the form (see: :attr:`use_form`) and the session (see:
        :attr:`use_session`).
        '''

        # initialze the form
        if self.use_form:
            self._create_form()

        # initialize the session
        if self.use_session:
            self._create_session()

    def _lifecycle(self):
        '''See :meth:`__call__` for when this method is called in the
        life cycle of a request.  This method is not implemented in
        the base class and raises :exc:`NotImplementedError`.
        '''
        raise NotImplementedError
    
    def _post_lifecycle(self):
        '''See :meth:`__call__` for when this method is called in the
        life cycle of a request.  The base class implementation
        garbage collects the form and session objects, if used (see:
        :attr:`use_form` and :attr:`use_session`).
        '''

        # clean up form
        if self.use_form and self.form is not None:
            self._cleanup_form()
            
        # clean up session
        if self.use_session and self.session is not None:
            self._cleanup_session()

    def _gen500(self, exc):

        '''Internal utility method used for generating debugging
        information when exceptions occur.
        '''
        
        tb = traceback.format_exc()
        self.log(tb)
        detail = (('<h3>%s</h3><pre>%s<hr>%s' % (exc, tb,
                                                 self.format_environ()))
                  if self.debug
                  else self.gen500msg)
        return HTTPInternalServerError(detail)

    def _create_form(self):
        'create the form'

        self.form = cgi.FieldStorage(fp=self.environ['wsgi.input'],
                                     environ=self.environ)

    def _cleanup_form(self):
        'garbage collect the form'
        
        self.form = None

    def _create_session(self):
        'create the session'

        sid = None
        
        # get a SignedCookie class with our session secret
        scc = self.__scc = signed_cookie_class(self.session_cookie_secret)

        # get the session cookie, if it exists
        if 'HTTP_COOKIE' in self.environ:
            cookies = scc(self.environ['HTTP_COOKIE'])
            sid = cookies.get(self.session_cookie_name)
            if sid: sid = sid.value

        backend = self.session_backend(self.session_backend_init)
        session = session_init(sid, backend, self.session_config)

        self.session = session

    def _cleanup_session(self):
        'save and garbage collect the session'

        session = self.session
        
        # save it
        session.save()
        # if expired() was called on the session, delete the cookie
        if session.expires == 1:
            self.del_cookie(self.session_cookie_name)
        # if it's a new session, set an outgoing cookie
        elif session.is_new:
            self.set_cookie(self.session_cookie_name, session.sid,
                            cookieclass=self.__scc)
        # garbage collect
        self.session = None
            

    @property
    def http_headers(self):
        '''An attribute for simplifying access to the incoming HTTP headers.
           Instead of writing this::

             host = self.environ["HTTP_HOST"]

           you can write this::

             host = self.http_headers.HOST

           I.e., keys you would normally look up in :attr:`environ` can
           be access as attributes of this object with ``HTTP_``
           stripped off the variable name.  (Actutally, the accessed
           attribute is looked up case-insensitively, so
           :attr:`self.http_headers.hOsT` also works.)

           Two headers that are not prefaced with ``HTTP_`` can also
           be accessed via this attribute: ``CONTENT_TYPE`` and
           ``CONTENT_LENGTH``, e.g., :attr:`self.http_headers.CONTENT_LENGTH`.

           .. note:: attributes are read-only.  You can not write,
                     e.g., ``self.http_headers.HOST = ...`` This will
                     raise an :exc:`AttributeError`.

           http_headers also supports the ``in`` operator::

             if "COOKIE" in self.http_headers:
                ...

           It also support iteration::

             for header, value in self.http_headers:
                ...
        '''

        h = self._db.get('http_headers')
        if h is not None:
            return h
        
        h = http_headers_helper(self.environ)
        self._db['http_headers'] = h
        return h

    @property
    def path_info_list(self):
        '''Read-only attribute to canonicalize :attr:`path_info` as a
        list.

        Splits :attr:`path_info` and returns it as a list.  Empty or all
        whitespace components or components == "." are ignored.
        
        '''

        return [p for p in self.path_info.split('/')
                if p.strip() and p != '.']


    def pop_path_info(self, count=1):
        '''Pops the left-most component off :attr:`path_info` and
        appends it to the end of :attr:`script_name`.  Returns the
        component popped and appended.  If count > 1, pops and appends
        that many components and returns a list of the components.  If
        count is less than one or greater than the number of
        components in :attr:`path_info`, then no action is taken and
        ``None`` is returned.  Examples: with::

           script_name = "/a/b/c"
           path_info = "/d/e/f"

        Then:
        
          ================   ===============   ==============   ============
          Calling            Returns           Values after call
          ----------------   ---------------   -----------------------------
          ..                                   script_name      path_info     
          ================   ===============   ==============   ============
          pop_path_info()    "d"               "/a/b/c/d"       "/e/f"        
          pop_path_info(2)   ["d", "e"]        "/a/b/c/d/e"     "/f"          
          pop_path_info(3)   ["d", "e", "f"]   "/a/b/c/d/e/f"   "/"           
          pop_path_info(4)   None              "/a/b/c"         "/d/e/f"      
          ================   ===============   ==============   ============  

        '''

        pil = self.path_info_list

        if count < 1 or count > len(pil):
            return None

        parts = pil[:count]
        sn = self.script_name
        if not sn or sn[-1] != '/':
            sn += '/'
        sn += '/'.join(parts)

        self.path_info = '/' + '/'.join(pil[count:])
        self.script_name = sn

        if count == 1:
            return parts[0]
        return parts

    @property
    def cookies(self):
        '''Attribute that processes the ``COOKIE`` header and returns
        a class representing the cookies.  Which class is used is
        defined by :attr:`cookieclass`.
        '''

        if 'cookies' in self._db:
            return self._db['cookies']

        c = self.cookieclass(self.http_headers.cookie)
        self._db['cookies'] = c
        return c

    def set_cookie(self, name, value, cookieclass=None, **attrs):
        '''Sets an outgoing cookie.

        :param name: the name of the cookie.
        :param value: its value.
        :param cookieclass: the class used to create the cookie.  If
                            ``None``, uses the class defined by
                            :attr:`cookieclass`.
        :param attrs: key/value pairs used to set attributes of the
                      cookie.  E.g., ``expires=3600``.
        '''

        cookieclass = cookieclass or self.cookieclass
        c = cookieclass()
        c[name] = value
        if attrs:
            c[name].update(attrs)
        self.response.headers['Set-Cookie'] = c[name].OutputString()
        
    def del_cookie(self, name):
        '''Deletes a cookie.

           Implemented by expiring the cookie; also sets the value to
           the empty string.
        '''

        c = Cookie.BaseCookie()
        c[name] = ''
        c[name]['expires'] = -3600
        self.response.headers['Set-Cookie'] = c[name].OutputString()
        

    def auth_with_mapping(self, mapping):
        '''Helper method used in HTTP Basic Authentication.

        :param mapping: any mapping that supports the standard
                        :meth:`dict.get` method, where the keys are
                        usernames and their values passwords.

        If the HTTP ``Authentication`` header does not have a
        username/password pair that is found in mapping
        :meth:`unauthorized` is called.
        '''

        user, pw = self.get_basic_auth()
        if user and pw and mapping.get(user) == pw:
            return
        self.unauthorized()

    def get_basic_auth(self):
        '''Helper method used in HTTP Basic Authentication.

        Retrieves username, password pair from HTTP ``Authentication``
        header.

        If the header does not exist, :meth:`unauthorized` is called.
        If the header exists, but the username/password pair cannot be
        base64 decoded, :exc:`HTTPBadRequest` is raised.  Otherwise, a tuple
        is returned: ``(username, password)``.

        '''

        if not self.environ.has_key('HTTP_AUTHORIZATION'):
            self.unauthorized()

        try:
            auth = self.environ['HTTP_AUTHORIZATION'][6:]
            user, pw = base64.decodestring(auth).split(':', 1)
        except:
            raise HTTPBadRequest

        return user, pw


    def unauthorized(self):
        '''Helper method used in HTTP Basic Authentication.
        
        Writes appropriate HTTP headers requesting authentication and
        raises :exc:`HTTPUnauthorized` exception.  This method does
        not return.
        '''

        unauthorized = HTTPUnauthorized()
        unauthorized.headers["WWW-Authenticate"] = ('Basic realm="%s"'
                                                   % self.auth_realm)
        raise unauthorized

    def redirect(self, uri, permanently=False):
        '''Send a redirect to the client.

        :param uri: The URI to relocate to.
        :param permanently: If False (the default) reply with 307,
                            *Moved Temporarily*, else 301,
                            *Moved Permanently*.

        This method does not return.
        '''

        if permanently:
            raise HTTPMovedPermanently(location=uri)
        else:
            raise HTTPTemporaryRedirect(location=uri)

    def subrequest(self, wsgiservlet, environ=None):
        '''Redirect internally.

        This does not send a redirect to the client (see
        :meth:`redirect`), but issues a subrequest to another servlet
        within the server.

        :param wsgiservlet: The servlet instance to pass control to.
        :param environ: If None (the default), a copy of
                        :attr:`self.environ` will be used in the
                        subrequest.  If a mapping, it will be merged
                        into a copy of :attr:`self.environ` and used
                        in the subrequest.

        .. note:: For subrequests, ``"wsgiservlets.subrequest"`` will
                  be found in the environment with value ``True``.

        This method does not return.
        '''

        assert isinstance(wsgiservlet, WSGIServlet)

        newenviron = dict(self.environ)
        if environ:
            newenviron.update(environ)

        newenviron['wsgiservlets.subrequest'] = True
        wsgiservlet(newenviron, None)

        # The above should never return, but just in case:
        raise RuntimeError, 'subrequest returned!'

    def log(self, msg):
        """Utility method to write a message to the error log,
        :attr:`envrion['wsgi.errors']`.

        :param str msg: The message to be written to the log.
        """

        log = self.environ['wsgi.errors']
        print >> log, ('[%s]  WSGIServlet [%s]: %s'
                       % (time.asctime(), self.__class__.__name__, msg))
        log.flush()

    def write(self, *args):
        '''Utility method to write the arguments to the client.
        
        :param args: tuple of arbitrary objects which will be
                     converted to strings.

        '''

        self.response.append(*args)
            
    def writeln(self, *args):
        '''Like :meth:`write`, but also append a newline.
        
        :param args: tuple of arbitrary objects which will be
                     converted to strings.

        '''

        self.response.append(*(args + ('\n',)))

    def format_environ(self, sep='\n'):
        '''Return the enivornment formatted: *key=val SEP key=val SEP ...*

        :param sep: the separation string inserted between key=value
                    paris.  Default: newline.
        '''
        
        
        env = []
        items = self.environ.items()
        items.sort()
        for k,v in items:
            env.append('%s=%s' % (k, v))
        return sep.join(env)

    def http_time(self, timestamp=None):
        """Return the current date and time formatted for a message header."""

        if timestamp is None:
            timestamp = time.time()

        return time.asctime(time.gmtime(timestamp))

    def send_file(self, path):
        """Sends the file specified by `path` as the response.  If
        `path` does not exist, :exc:`HTTPNotFound` is raised.  If
        `path` is not a file, :exc:`HTTPForbidden` is raised.
        Otherwise, :exc:`HTTPOK` is raised with the content of the
        file as the response and Content-Type is set based on
        path's extension.  This method does not return.
        """

        if not os.path.exists(path):
            raise HTTPNotFound

        if not os.path.isfile(path):
            raise HTTPForbidden

        f = open(path)
        response = HTTPOK(f)

        fs = os.fstat(f.fileno())
        response.set_content_type_by_filename(path)
        response.headers["Content-Length"] = str(fs[6])
        response.headers["Last-Modified"] = self.http_time(fs.st_mtime)

        raise response

    @classmethod
    def test_server(servlet_class, host='', port=8000, forever=True,
                    *args, **kw):
        """Create a test server.  

        :param str host: the host to bind the server.  An empty string
                         (the default) binds to all interfaces.
        :param int port: the port to bind the server.  The default is 8000.
        :param bool forever: when ``True`` (the default) listen for
                             connections forever; when ``False``
                             accept one connection then exit.
        :param args,kw: passed to servlet constructor when creating
                        an instance.

        This method, using :func:`wsgiref.simple_server.make_server`
        from the standard python library, creates a HTTP server.  This
        is very handy when doing quick prototyping of a new class,
        e.g::

            class MyPage(HTMLPage):
                ...

            if __name__ == '__main__':
                MyPage.test_server()

        After executing the above, you can use your browser and visit
        `http://localhost:8000/`.
        """

        from wsgiref.simple_server import make_server

        # get instance
        servlet = servlet_class(*args, **kw)
        #make server
        server = make_server(host, port, servlet)

        # run forever or just once
        if forever:
            server.serve_forever()
        else:
            server.handle_request()

                
Servlet = WSGIServlet

######################################################################

