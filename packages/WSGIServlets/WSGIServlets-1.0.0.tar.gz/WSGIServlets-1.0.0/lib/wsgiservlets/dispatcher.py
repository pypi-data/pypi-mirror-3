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

import sys
import os

from wsgiservlets.wsgiservlet import *
from wsgiservlets.httpresponse import *

__all__ = ['Dispatcher']

class Dispatcher(WSGIServlet):
    '''Dispatcher does not generate any content, but is a dispatching
    agent in the truest sense: incoming requests are processed and
    passed on to another agent which handles the request. Dispatchers
    determine how to pass on the request by examining PATH_INFO and
    provide a means to intermix several servlets along with static
    file content under the control of one servlet.
    '''

    default_config = {
        'default_servlet' : 'index',
        'dirindex' : ('index.html', 'index.htm'),
        'forbid_startswith' : ('.', '_'),
        'forbid_extensions' : ('.py', '.pyc', '.pyo', '.wsgi'),
        }
    '''A mapping that holds variables which control dispatching
    behaviour:

      * **default_servlet** (str) -- if ``PATH_INFO`` is empty,
        attempt a redirect to this servlet.  (default: ``"index"``)
        

      * **dirindex** (seq) -- a sequence of file names to be searched
        (in order of the seq) when PATH_INFO references a directory.
        (default: ``("index.html", "index.htm")``)

      * **forbid_startswith** (seq) -- a sequence of filename prefixes
        which are forbidden in any one component of the path.
        (default: ``(".", "_")``)
      

      * **forbid_extensions** (seq) -- a sequence of file extensions
        which are forbidden. (default: ``(".py", ".pyc", ".pyo",
        ".wsgi")``)

    '''
    
    def __init__(self, docroot=None, servlet_mapping = {},
                 **user_config):

        '''
        :param docroot: the path to the document root containing
          static content. This must be an existing directory.  If
          ``None`` (the default), static content serving will be
          disabled.
        :type docroot: str or None
        :param dict servlet_mapping: a mapping of names to servlet
          classes of the form::

             name : WSGIServletClass
             
          or::

             name : (WSGIServletClass, args [, kw])

          In the first form, the name maps to a WSGIServlet class (not
          an instance). In the second, a tuple is specified with args,
          a tuple, and kw, a dict, the positional parameters and
          keyword arguments, respectively, to be passed to the
          constructor of the servlet class. If not specified, args
          defaults to an empty tuple and kw an empty dict.
        :param user_config: extra keyword arguments will be merged
          with :attr:`default_config` to modify behaviour of the
          dispatcher.


        After a dispatcher receives a request, PATH_INFO is inspected
        and the first component (i.e., ``path_info_list[0]``), if it
        exists, is looked up in servlet_mapping and if a servlet is
        found an instance is created::

            servlet = WSGIServletClass(*args, **kw)
            
        :meth:`WSGIServlet.pop_path_info` is called to shift the
        servlet name to ``SCRIPT_NAME``, then
        :meth:`WSGIServlet.subrequest` is called on the servlet
        instance, processing the request and returning the results to
        the client.

        If a servlet class is not found in servlet_mapping, it is
        assumed PATH_INFO refers to a static file relative to
        :attr:`docroot`. If such a file exists, the file is returned
        as the content.

        If no mapping is found and no file is found (or
        :attr:`docroot` was never specified), :exc:`HTTPNotFound` is
        raised.

        .. note:: servlets handling requests on behalf of a Dispatcher
           will have in their environment a key,
           ``"wsgiservlets.dispatcher"``, with value the Dispatcher
           instance.
        '''

        # if docroot is specified, make sure it is an existing
        # directory
        self.docroot = None
        if docroot:
            if not os.path.isdir(docroot):
                raise IOError, '%s is not an existing directory' % docroot
            self.docroot = os.path.abspath(docroot)

        # validate servlet_mapping has proper SCRIPT_NAMES as keys and
        # WSGIServlets as values
        for sn, klassdef in servlet_mapping.iteritems():
            assert (len(sn) > 1
                    and '/' not in sn), 'Illegal SCRIPT_NAME'

            try:
                klass, args, kw = klassdef
            except TypeError:
                # klassdef was not a tuple, so assume it's just the
                # WSGIServlet subclass
                klass, args, kw = klassdef, (), {}
            except ValueError:
                # was not a seq of three elem, so we'll assume it was
                # two, the WSGIServlet subclass and the args.  If this
                # throws an error we'll let it propagate
                klass, args = klassdef
                kw = {}
                
            assert issubclass(klass, WSGIServlet), \
                   'SCRIPT_NAME must map to subclass of WSGIServlet'

            assert type(args) is tuple, \
                   'args for Dispatcher WSGI App instantiation must be a tuple'

            assert type(kw) is dict, \
                   'kw for Dispatcher WSGI App instantiation must be a dict'

            servlet_mapping[sn] = klass, args, kw

        self.servlet_mapping = servlet_mapping
        
        config = dict(Dispatcher.default_config)
        config.update(user_config)
        self.config = config

    def _pre_lifecycle(self):
        pass
    
    def _post_lifecycle(self):
        pass
    
    def _lifecycle(self):

        # search for a script_name in the environ
        pil = self.path_info_list
        sname = pil[0] if pil else None

        if not sname:
            # No script_name...use the default (if defined) and
            # redirect to it
            default = self.config['default_servlet']
            if default:
                qs = self.query_string
                if qs: qs = '?' + qs
                self.redirect(os.path.join(self.script_name, default) + qs)
                # does not return

        servlet = self.servlet_mapping.get(sname)
        if servlet:
            # we have a servlet...do a subrequest
            servlet, args, kw = servlet
            self.pop_path_info()
            self.subrequest(servlet(*args, **kw),
                            {'wsgiservlets.dispatcher': self})
            # does not return

        # do we have a docroot defined?
        if self.docroot:
            pi = self.path_info
            if pi: pi = pi[1:]
            self._fetch(pi)
            # does not return
            
        raise HTTPNotFound
    

    def _fetch(self, relpath):

        """Fetch a file.

        :param relpath: the path of the file, relative to self.docroot
        
        """

        # make sure normalized path is under docroot
        path = os.path.normpath(os.path.join(self.docroot, relpath))
        if os.path.commonprefix([self.docroot, path]) != self.docroot:
            raise HTTPForbidden
        
        # if path is a directory, search it for files in
        # config['dirindex'] redirecting to the first one found.
        if os.path.isdir(path):
            for index in self.config['dirindex']:
                fname = os.path.join(path, index)
                if os.path.isfile(fname):
                    p = os.path.join(self.script_name or '/', relpath, index)
                    self.redirect(p)

        # if it's a file make sure no component of the path begins
        # with a forbidden prefix or ends with a forbidden extension
        elif os.path.isfile(path):

            for comp in path.split('/'):
                basename = os.path.basename(comp)
                root, ext = os.path.splitext(basename)
                if ext in self.config['forbid_extensions']:
                    raise HTTPForbidden
                for prefix in self.config['forbid_startswith']:
                    if root.startswith(prefix):
                        raise HTTPForbidden
            # It's OK
            self.send_file(path)
            # does not return

        raise HTTPNotFound
