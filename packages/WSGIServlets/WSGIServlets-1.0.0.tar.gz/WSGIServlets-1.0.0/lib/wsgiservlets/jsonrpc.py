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

import json

from wsgiservlets.wsgiservlet import *
from wsgiservlets.httpresponse import *

__all__ = ['JSONRPCServer']

class JSONRPCServer(WSGIServlet):
    """`JSON-RPC <http://groups.google.com/group/json-rpc>`_ is a
    remote procecure call protocol using `JSON <http://www.json.org>`_
    for encoding messages between client and server.

    :class:`JSONRPCServer` is a WSGIServlet providing JSON-RPC
    services to clients.

    Any method with prefix ``rpc_`` is available to be called by a
    client (which should call the method without the prefix).  Any
    method *not* prefixed with ``rpc_`` is **not** available to
    clients and becomes a private method of the server implementation.
    
    Here's an example servlet with one private method and one public
    method::

            from wsgiservlets import JSONRPCServer

            class myrpcserver(JSONRPCServer):

                def priv(self):
                    # this method could not be called from a client
                    # because it does not begin with *rpc_*
                    pass

                def rpc_echo_upper(self, s):

                    # this method is available to clients as
                    # **echo_upper(str)**

                    return s.upper()                                 

    The tutorial that comes with WSGIServlets has an example of
    JSONRPCServer in action.

    """

    # will be mapping of callables
    rpcmethods = None

    def _pre_lifecycle(self):
        pass

    def _post_lifecycle(self):
        pass

    def _lifecycle(self):

        # JSON-RPC only uses POST
        if self.method != 'POST':
            raise HTTPMethodNotAllowed()

        # Content-Length
        clength = self.http_headers.content_length
        clength = int(clength) if clength else -1

        # Read the JSON
        json = self.environ['wsgi.input'].read(clength)

        if self.debug:
            self.log('Received JSON: %s' % json)
            
        # Dispatch and write out response
        self.writeln(self._dispatch(json))

        # Set Content-Type and Cache-Control
        resp = self.response
        resp.content_type = 'application/json'
        resp.headers['Cache-Control'] = 'no-cache'

    def _init_rpcmethods(self):

        'Search for instance methods with prefix "rpc_"'

        import types
        
        results = []
        for key in dir(self):
            # only consider "rpc_" prefixed attrs
            if key[:4] == 'rpc_' and len(key) > 4:

                # get the attr and see if it's a method of this instance
                value = getattr(self, key)
                if (isinstance(value, types.MethodType)
                    and value.im_self == self):

                    # append to list stripping prefix
                    results.append((key[4:], value))

        self.rpcmethods = dict(results)


    def _dispatch(self, json_str):

        '''Take json as input, the request (or batch of requests), and
        generate a response (or batch of responses) and dispatch them
        to registered methods.  Returns json (string) if there is a
        response or an empty string if the request was a notification
        (or batch of notifications).
        '''

        if self.rpcmethods is None:
            self._init_rpcmethods()

        try:
            # try to convert json input into python object
            try:
                req = json.loads(json_str)
            except Exception, e:
                raise ParseError(str(e))

            # is it a batch request?
            if isinstance(req, list):

                # no requests in the batch?
                if len(req) == 0:
                    raise InvalidRequest()

                # create list of requests
                batch = []
                for r in req:
                    batch.append(request(r, self.rpcmethods))

                # get list of responses
                resp = [resp for resp in
                        [req.response() for req in batch]
                        if resp]
            else:
                # a single request
                resp = request(req, self.rpcmethods).response()

        except JSONRPCError, e:
            # generate error response
            resp = response(id=None, jsonrpc="2.0",
                            result=None, error=e)

        # maybe it was a notification or a batch of notifications, so
        # we do this conditionally
        if resp:
            try:
                json_str = json.dumps(resp)
            except Exception, e:
                # was it the result or error?  (assuming it wasn't id
                # or jsonrpc).  We'll brute-force delete both and add
                # an error.
                resp.pop('result', None)
                resp.pop('error', None)
                resp['error'] = InternalError(str(e)).error_object()
                json_str = json.dumps(resp)
                
            return json_str

        return ''


class request(object):

    def __init__(self, req, methods):

        '''convert json Object (represented in python form, as a dict,
        not json string) to an instance of request.  Use methods as
        the mapping (name=>method) of known methods.  
        '''

        # establish some defaults
        self.id = None
        self.jsonrpc = "2.0"
        self.result = None
        self.error = None
        
        try:
            # the request should be a dict
            if not isinstance(req, dict):
                raise InvalidRequest('request must be an Object')

            # check id; we do this as early as possible so we know
            # whether or not to inform clients of errors (Notification
            # errors are not returned to client).
            self.id = id = req.pop('id', NotFound)
            if id is not NotFound and isinstance(id, (dict, list, bool)):
                raise InvalidRequest('id must be a string, number or NULL')

            # check version
            jsonrpc = req.pop('jsonrpc', NotFound)
            if jsonrpc is NotFound:
                self.jsonrpc = jsonrpc = "1.0"
            else:
                if jsonrpc != "2.0":
                    raise InvalidRequest('jsonrpc, if specified, must be "2.0"')
                self.jsonrpc = jsonrpc
            
            # check params
            params = req.pop('params', NotFound)
            if params is NotFound:
                params = []
            else:
                if jsonrpc == "2.0" and not isinstance(params, (list, dict)):
                    raise InvalidRequest('params must be an Array or Object')
                elif not isinstance(params, list):
                    raise InvalidRequest('params must be an Array')
            self.params = params
            
            # check method
            method = req.pop('method', NotFound)
            if method is NotFound:
                raise InvalidRequest('no method specified')
            if method not in methods:
                raise MethodNotFound(method)
            self.method = methods[method]
            
            # if there are any other members in req we have an invalid
            # request
            if req:
                unknowns = ', '.join(req.keys())
                raise InvalidRequest('invalid members: ' + unknowns)
            
        except JSONRPCError, e:
            self.error = e
        except:
            raise RuntimeError, 'Programming error: should not reach here!'
            

    def response(self):

        # an error may have occurred in the constructor
        if self.error:
            return response(self.id, self.jsonrpc,
                            None, self.error)

        try:
            if isinstance(self.params, list):
                result = self.method(*self.params)
            else:
                result = self.method(**self.params)
        except Exception, e:
            return response(self.id, self.jsonrpc,
                            None, InternalError(str(e)))

        return response(self.id, self.jsonrpc, result, None)

class response(dict):
    '''
    Response is a dict with special constructor to check values.
    '''

    def __init__(self, id, jsonrpc, result, error):

        v2 = jsonrpc == "2.0"
        self.notification = n = ((v2 and id is NotFound)
                                 or (not v2 and id is None))
        # if we're a notification, just return
        if n: return

        if id is NotFound:
            id = None
        if error:
            error = error.error_object()

        if v2:
            dict.__init__(self, id=id, jsonrpc=jsonrpc)
            if error:
                self['error'] = error
            else:
                self['result'] = result
        else:
            dict.__init__(self, id=id, result=result, error=error)

    def __nonzero__(self):
        # notifications are False
        return not self.notification

class NotFound:

    '''Used as singleton to distinguish None from absent members in
       mappings, e.g., value = mapping.get("somekey", NotFound).
       Useful when None is a valid value for "somekey".
    '''

    def __nonzero__(self):
        return False
    def __str__(self):
        return 'NotFound'
    __repr__ = __str__
NotFound = NotFound()
    
class JSONRPCError(Exception):

    def __init__(self, detail=None, **data):
        
        if self.__class__ == JSONRPCError:
            raise RuntimeError, 'JSONRPCError is an abstract base class'

        if detail:
            data['detail'] = detail
        self.data = data

    def error_object(self):
        
        e = dict(code = self.code,
                 message = self.message)
        if self.data:
            e['data'] = self.data
        return e

class ParseError(JSONRPCError):
    code = -32700
    message = 'Parse Error'
class InvalidRequest(JSONRPCError):
    code = -32600
    message = 'Invalid Request'
class MethodNotFound(JSONRPCError):
    code = -32601
    message = 'Method Not Found'
class InvalidParams(JSONRPCError):
    code = -32602
    message = 'Invalid Params'
class InternalError(JSONRPCError):
    code = -32603
    message = 'Internal Error'
