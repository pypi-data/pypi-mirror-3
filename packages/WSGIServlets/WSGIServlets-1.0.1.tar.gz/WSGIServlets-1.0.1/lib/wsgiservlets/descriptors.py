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

import cgi

from wsgiservlets.constants import *

__all__ = ['GET_var', 'POST_var', 'environ_helper', 'http_headers_helper',
           'servletmeta']

class servletmeta(type):

    'Metaclass for WSGIServlets'
    
    def __init__(cls, name, bases, dictionary):

        # in coordination with {GET|POST}_var non-data descriptors,
        # stuff the name of the instance variable into the instance of
        # the descriptor so it knows its own name.
        for k,v in dictionary.iteritems():
            if isinstance(v, METHOD_var):
                v.name = k

class METHOD_var(object):

    '''Non-data descriptor: delegate an attribute to the key of the
    underlying cgi.FieldStorage.

    For use with WSGIServlet only.  That class has a metaclass which
    is required for full functionality.

    '''

    @property
    def default_only_when_not_post(self):
        raise NotImplementedError

    def __init__(self, default='', conv=None, escape=cgi.escape):

        # test default is a proper value
        assert isinstance(default, (list, dict, str)), \
               ('Default value must be a string,'
                'list or dict (or subclass thereof)')

        if isinstance(default, list):
            for i in default:
                assert isinstance(i, str), ('Default values of lists must '
                                            'have elements of strings only')
        if isinstance(default, dict):
            for k,v in default.iteritems():
                assert type(k) is str, ('Default keys of dicts must '
                                        'be strings')
                assert isinstance(v, (str, list)), \
                       ('Default values of dicts must have values of lists '
                        'or strings')
                if isinstance(v, list):
                    for i in v:
                        assert isinstance(i, str), ('Default values of lists must '
                                                    'have elements of strings only')
        # conv must be None or callable
        assert conv is None or callable(conv), ('Argument conversion must '
                                                'be None or callable')
        # test conversion method works without exception on default
        if conv:
            try:
                conv(default)
            except Exception, msg:
                raise AssertionError, ('Argument conversion method failed '
                                       'on default value: %s' % msg)
        # assert escape is a callable
        assert callable(escape), 'Argument escape must be a callable'
        
        self.name = None # <-- to be filled in by metaclass
        self.default = default
        self.conv = conv
        self.escape = escape

    def __get__(self, obj, objtype=None):

        if obj is None:
            return self

        if self.name in obj._db:
            return obj._db[self.name]

        default_only = self.default_only_when_not_post and obj.method != 'POST'
        name = self.name
        default = self.default
        conv = self.conv
        escape = self.escape

        if isinstance(default, list):
            if default_only:
                # use a copy of the default
                val = default[:]
            else:
                # use the list of stripped strings
                val = [escape(x.strip()) for x in obj.form.getlist(name)]

        elif isinstance(default, dict):

            # start with a copy of the dict, so any keys not
            # in the form will have their default
            val = default.copy()
            if not default_only:
                # iterate over every key in the form
                for var in obj.form.keys():
                    # see if it is a dict RE and the current self.name
                    m = DICTVAR.match(var) or IMAGEVAR.match(var)
                    if m and m.group(1) == name:
                        # get the key from the match
                        key = m.group(2)
                        if isinstance(val.get(key), list):
                            # this item is a list
                            val[key] = [escape(x.strip()) for x in
                                        obj.form.getlist(var)]
                        else:
                            # this item is a string
                            val[key] = escape(obj.form.getfirst(var).strip())
        else:
            # default is a string
            if default_only:
                val = default
            else:
                val = escape(obj.form.getfirst(name, default).strip())

        if conv:
            try:
                val = conv(val)
            except:
                val = conv(default)

        # save the value for future use so it doesn't have to be
        # computed a second time.
        obj._db[name] = val
        
        return val

    def __set__(self, obj, val):
        obj._db[self.name] = val

    def __delete__(self, obj):
        raise AttributeError, ('Cannot delete %s from instance of %s'
                               % (self.name, obj.__class__.__name__))

class GET_var(METHOD_var):
    'METHOD_var for GET requests'
    
    default_only_when_not_post = False

class POST_var(METHOD_var):
    'METHOD_var for POST requests'
    
    default_only_when_not_post = True


class environ_helper(object):
    '''A descriptor used with WSGIServlet instances which will
    access/set its value in the underlying environ mapping of the
    servlet.  E.g.::

       class MyServlet(WSGIServlet):

           server = eniron_helper("SERVER_NAME")

    Instances of MyServlet can use attribute :attr:`server` to read or
    set :attr:`environ["SERVER_NAME"]`.
    '''

    def __init__(self, key, default=''):
        self.key = key
        self.default = default

    def __get__(self, obj, objtype=None):

        if obj is None:
            return self

        return obj.environ.get(self.key, self.default)

    def __set__(self, obj, val):

        obj.environ[self.key] = val

    def __delete__(self, obj):

        del obj.environ[self.key]
        
######################################################################

class http_headers_helper(object):
    'See: :meth:`WSGIServlet.http_headers`'

    def __init__(self, environ):
        object.__setattr__(self, 'environ', environ)
        
    def __getattribute__(self, name):

        name = name.upper()
        if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            name = 'HTTP_' + name
        return object.__getattribute__(self, 'environ').get(name)

    def __setattr__(self, name, value):
        raise AttributeError, "can't set attribute"

    def __delattr__(self, name):
        raise AttributeError, "can't delete attribute"


    def __iter__(self):

        environ = object.__getattribute__(self, 'environ')

        for k,v in environ.iteritems():
            if k in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                k = k.lower()
            elif k[:5] == 'HTTP_':
                k = k[5:].lower()
            else:
                continue
            yield k,v

    def __contains__(self, name):

        return getattr(self,name.replace('-','_'),None) is not None
