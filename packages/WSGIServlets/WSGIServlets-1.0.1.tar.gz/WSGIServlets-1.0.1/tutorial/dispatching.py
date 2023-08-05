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


from TutorialBase import *

class dispatching(HTMLPage):

    "How to mix servlets and static content under one servlet."

    title = 'The Dispatcher'

    def write_content(self):

        self.writeln(OVERVIEW)



# -*-*- DOC -*-*-



OVERVIEW = make_overview("""
Up to this point we have been looking at functionality provided by
`HTMLPage`, the servlet for creating HTML content, and `WSGIServlet`,
the base class for all servlets.  There are two other subclasses of
`WSGIServlet` that come with the standard distribution of
wsgiservlets:

  1. `Dispatcher`, which allows you to mix several servlets and static
      content under the control of one servlet.  This whole tutorial
      is an example of dispatching.
  2. `JSONRPCServer`, which aids in creating JSON-RPC services.

This servlet will review `Dispatcher`.  The next servlet will review
`JSONRPCServer`.


* * *


## Dispatcher

`Dispatcher` does not generate any content, but is a dispatching agent
in the truest sense: incoming requests are processed and passed on to
another agent which handles the request.  Dispatchers determine how to
pass on the request by looking at `PATH_INFO`.
      
When constructing a `Dispatcher` you need to pass in one or both of
the following keyword arguments to the constructor:

  1. `docroot`, a string, the path to the document root containing static
      content.  This must be an existing directory.
  2. `servlet_mapping`, a mapping of names to servlet classes of the
      form:

> *name* => `WSGIServletClass`  
> or   
> *name* => `(WSGIServletClass, args [, kw])`

In the first form, the name maps to a `WSGIServlet` *class* (not an
instance).  In the second, a tuple is specified with `args`, a tuple,
and `kw`, a dict, the positional parameters and keyword arguments,
respectively, to be passed to the constructor of the servlet class.
If not specified, `args` defaults to an empty tuple and `kw` an empty
dict.

After a dispatcher receives a request, `PATH_INFO` is inspected and the
first component (i.e., `path_info_list[0]`), if it exists, is looked
up in `servlet_mapping` and if a servlet is found an instance is
created:

        servlet = WSGIServletClass(*args, **kw)

Then `subrequest` is called on the servlet instance, processing the
request and returning the results to the client.  See the reference
documentation for details about making subrequests.

If a servlet class is not found in `servlet_mapping`, it is assumed
`PATH_INFO` refers to a static file relative to `docroot`.  If such a
file exists, the file is returned as the content.

If no mapping is found and no file is found (or `docroot` was never
specified), `HTTPNotFound` (a 404) is raised.

There are other configuration options you can specify when creating
your dispatcher: 1) a default servlet if `PATH_INFO` is empty, 2) the
directory index files to search for if the referenced static file is a
directory (e.g., `index.html`), 3) what static files to forbid access
to when requested (raising `HTTPForbidden`).  Forbidding certain files
based on filename patterns allows you to co-locate source code with
static files without worry of exposing your source to the WWW.

See the reference documentation for details about configuring your
dispatcher and look at the tutorial implementation as an example.

""")

