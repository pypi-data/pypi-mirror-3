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

import os
from cStringIO import StringIO
import mimetypes

class dictlist(dict):

    def __setitem__(self, key, value):
        l = self.get(key)
        if l is None:
            l = []
            dict.__setitem__(self, key, l)
        l.append(value)

    def items_expand(self):
        r = []
        for k,l in dict.iteritems(self):
            for v in l:
                r.append((k,v))
        return r

    def clear(self, key):
        del self[key][:]
        
class HTTPResponse(Exception):

    'Abstract base class for HTTP Responses.'

    # each non-abstract subclass MUST set these three values:
    code = -1 # http response status code value
    'The HTTP status code'
    title = 'Response Title'
    'The title of the response'
    # not currently implemented
    description = ''
    

    # a subclass may set this
    _body_tmpl = '''<html>
<head>
  <title>{status}</title>
</head>
<body>
  <h1>{status}</h1>
  {description}
  <hr>
  {detail}
</body>
</html>
'''

    if not mimetypes.inited:
        mimetypes.init()
    types_map = dict(mimetypes.types_map)

    def __init__(self, detail=''):
        '''An HTTP response is constructed by specifying, optionally,
        detail which becomes the body of the response.  If *detail* is
        an open file object, then the response body will be the
        content of the file.  If it is a string, a :class:`StringIO`
        will be used as the body and will be seeded with the string.
        If empty (the default), an empty :class:`StringIO` will be
        used.  In the later cases (where :class:`StringIO` is used),
        output can be appended to the body with calls to
        :meth:`append`.

        :param detail: default: an empty string
        :type detail: str or file

        '''
        
        if self.__class__ is HTTPResponse:
            raise RuntimeError, 'HTTPResponse is an abstract base class'
        
        self.__headers = dictlist()
        self.__content_type = None

        if type(detail) is file:
            self.__body = detail
        elif detail:
            self.__body = StringIO(self.__gen_default_body(detail))
            self.__body.seek(0, os.SEEK_END)
        else:
            self.__body = StringIO()

        self.close = self.__body.close

    def __gen_default_body(self, detail):
        return self._body_tmpl.format(status=self.status,
                                      description=self.description,
                                      detail=detail)

    def __call__(self, start_response):

        self.headers['Content-Type'] = self.content_type
        start_response(self.status, self.headers.items_expand())
        return self
        
    def __iter__(self):

        body = self.__body
        if type(body) is not file:
            if body.tell() == 0:
                body.write(self.__gen_default_body(''))
            body.seek(0)
        return body

    def __get_ct(self):
        '''The Content-Type of the response.  If never explicitly set,
        the Content-Type will be taken from
        :attr:`default_content_type`.
        
        '''
        
        return self.__content_type or self.default_content_type

    def __set_ct(self, val):
        self.__content_type = val

    content_type = property(fget=__get_ct, fset=__set_ct)

    def set_content_type_by_filename(self, path):
        'Sets the Content-Type header based on the path extenstion.'

        rest, ext = os.path.splitext(path)
        self.content_type = self.types_map.get(ext, 'application/octet-stream')

    def append(self, *args):
        'Appends each arg (converted to str) to the body.'
        
        self.__body.writelines([str(s) for s in args])

    @property
    def default_content_type(self):
        'The default Content-type, "text/html"'
        return 'text/html'

    @property
    def status(self):
        'The response status as string generated from code and title'
        return '%d %s' % (self.code, self.title)
    
    @property
    def headers(self):
        'The response headers, as a dict'
        return self.__headers

class HTTPContinue(HTTPResponse):
    code = 100
    title = "Continue"

class HTTPSwitchingProtocols(HTTPResponse):
    code = 101
    title = "Switching Protocols"

class HTTPOK(HTTPResponse):
    code = 200
    title = "OK"

class HTTPCreated(HTTPResponse):
    code = 201
    title = "Created"

class HTTPAccepted(HTTPResponse):
    code = 202
    title = "Accepted"

class HTTPNonAuthoritativeInformation(HTTPResponse):
    code = 203
    title = "Non-Authoritative Information"

class HTTPNoContent(HTTPResponse):
    code = 204
    title = "No Content"

class HTTPResetContent(HTTPResponse):
    code = 205
    title = "Reset Content"

class HTTPPartialContent(HTTPResponse):
    code = 206
    title = "Partial Content"

class HTTPRedirect(HTTPResponse):
    'base class for redirections'

    def __init__(self, location):
        HTTPResponse.__init__(self)
        self.headers['Location'] = location

class HTTPMultipleChoices(HTTPRedirect):
    code = 300
    title = "Multiple Choices"

class HTTPMovedPermanently(HTTPRedirect):
    code = 301
    title = "Moved Permanently"

class HTTPFound(HTTPRedirect):
    code = 302
    title = "Found"

class HTTPSeeOther(HTTPRedirect):
    code = 303
    title = "See Other"

class HTTPNotModified(HTTPRedirect):
    code = 304
    title = "Not Modified"

class HTTPUseProxy(HTTPRedirect):
    code = 305
    title = "Use Proxy"

class HTTPUnused(HTTPResponse):
    code = 306
    title = "Unused"

class HTTPTemporaryRedirect(HTTPRedirect):
    code = 307
    title = "Temporary Redirect"

class HTTPBadRequest(HTTPResponse):
    code = 400
    title = "Bad Request"

class HTTPUnauthorized(HTTPResponse):
    code = 401
    title = "Unauthorized"

class HTTPPaymentRequired(HTTPResponse):
    code = 402
    title = "Payment Required"

class HTTPForbidden(HTTPResponse):
    code = 403
    title = "Forbidden"

class HTTPNotFound(HTTPResponse):
    code = 404
    title = "Not Found"
    
class HTTPMethodNotAllowed(HTTPResponse):
    code = 405
    title = "Method Not Allowed"

class HTTPNotAcceptable(HTTPResponse):
    code = 406
    title = "Not Acceptable"

class HTTPProxyAuthenticationRequired(HTTPResponse):
    code = 407
    title = "Proxy Authentication Required"

class HTTPRequestTimeOut(HTTPResponse):
    code = 408
    title = "Request Time-out"

class HTTPConflict(HTTPResponse):
    code = 409
    title = "Conflict"

class HTTPGone(HTTPResponse):
    code = 410
    title = "Gone"

class HTTPLengthRequired(HTTPResponse):
    code = 411
    title = "Length Required"

class HTTPPreconditionFailed(HTTPResponse):
    code = 412
    title = "Precondition Failed"

class HTTPRequestEntityTooLarge(HTTPResponse):
    code = 413
    title = "Request Entity Too Large"

class HTTPRequestUriTooLarge(HTTPResponse):
    code = 414
    title = "Request-URI Too Large"

class HTTPUnsupportedMediaType(HTTPResponse):
    code = 415
    title = "Unsupported Media Type"

class HTTPRequestedRangeNotSatisfiable(HTTPResponse):
    code = 416
    title = "Requested Range Not Satisfiable"

class HTTPExpectationFailed(HTTPResponse):
    code = 417
    title = "Expectation Failed"

class HTTPInternalServerError(HTTPResponse):
    code = 500
    title = "Internal Server Error"

class HTTPNotImplemented(HTTPResponse):
    code = 501
    title = "Not Implemented"

class HTTPBadGateway(HTTPResponse):
    code = 502
    title = "Bad Gateway"

class HTTPServiceUnavailable(HTTPResponse):
    code = 503
    title = "Service Unavailable"

class HTTPGatewayTimeOut(HTTPResponse):
    code = 504
    title = "Gateway Time-out"

class HTTPVersionNotSupported(HTTPResponse):
    code = 505
    title = "HTTP Version not supported"



### build __all__ to be HTTPResponse and all it's subclasses and build
### responses_map to be a mapping of status code to response class
__all__ = ['http_responses_map']
http_responses_map = {}
for name, value in globals().items():
    if isinstance(value, type) and issubclass(value, HTTPResponse):
        __all__.append(name)
        if value.code != -1:
            http_responses_map[value.code] = value

