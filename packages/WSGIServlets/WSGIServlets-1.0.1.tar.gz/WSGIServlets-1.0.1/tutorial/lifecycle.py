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

class lifecycle(HTMLPage):

      'An explanation of the lifecycle of a request.'

      title = 'Request Life-Cycle'

      def write_content(self):
            self.writeln(OVERVIEW)



# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
It is assumed you have an understanding of WSGI applications and how
they are called by servers and gateways.  If you're not familiar with
WSGI, I recommend you review [PEP
3333](http://www.python.org/dev/peps/pep-3333/) now.

____

In the [first tutorial](index) it was mentioned `HTMLPage` subclasses
`WSGIServlet`.  To exploit the full power of servlets it is
recommended you have a solid understanding of the following code:

<pre class="codesample">
 1. class WSGIServlet(object):
 2. 
 3.     def __call__(self, environ, start_response):
 4.
 5.         try:
 6.             self._pre_lifecycle()
 7.             self._lifecycle()
 8.         finally:
 9.             self._post_lifecycle()
10.         return ...
11.
12.     def _pre_lifecycle(self):
13.        ...
14. 
15.     def _lifecycle(self):
16.        raise NotImplementedError
17.
18.     def _post_lifecycle(self):
19.         ...
</pre>

With your knowledge of how WSGI works, you can see instances of
WSGIServlet are callable and their signature follows the protocol of
WSGI applications.  For each request processed by a servlet, a series
of methods is called on the servlet in a specific order.  The above
simplified code illustrates what happens: in lines 5-10, in a `try`
statement, the following methods are called in order:

        _pre_lifecycle() ===> _lifecycle() ===> _post_lifecyce()


  * **_pre_lifecycle()**: The base class implementation initializes
      the `form` and `session` attributes, making them available for
      `_lifecycle()`.

  * **_lifecycle()**: This is where the real work of a servlet
      happens, generating the response sent back to the client.  Note,
      however, the base class raises `NotImplementedError`, making it
      an Abstract Base Class.  WSGIServlets comes with three
      subclasses implementing `_lifecycle`: `HTMLPage`, which is this
      tutorial's focus, `JSONRPCServer`, a servlet creating json-rpc
      services (a tutorial is coming up) and `Dispatcher`, a servlet
      which allows mixing many servlets along with static content
      under one servlet (this tutorial is an example of such an
      application).

  * **_post_lifecycle()**: The base class implementation garbage
      collects `form` and, if `session` was used, saves the session
      state and garbage collects `session`.

Creating a new type of servlet is a matter of subclassing
`WSGIServlet` and, minimally, implementing `_lifecycle`.  This is how
`HTMLPage` implements `_lifecycle`:

<pre class="codesample">
 1.   def _lifecycle(self):
 2.       try:
 3.           self.prep()
 4.           if not self.write_html():
 5.               raise HTTPNoContent
 6.       finally:
 7.           self.wrapup()
</pre>

  * `prep` is called to do any pre-processing, before generating the
  response.  The base class method is a no-op.  This is a good place
  to validate incoming data, open database connections, initialize
  variables for the request, etc.  Note the return value is ignored.

  * `write_html` is where the response is generated and output written
  to the client.  Typically, you will not need to override this
  method.  The next servlet in the tutorial will cover what happens in
  `write_html`.  Note how the return value, if false, raises
  `HTTPNoContent`.  Raising exceptions for preemptive returns will be
  covered later.

  * `wrapup` is where any necessary post-processing occurs.  The base
  class method is a no-op.  Here is the place to do any clean-up of
  external connections, conditionally invalidate sessions, etc.  Note
  the return value is ignored.

The next servlet will review the functionality of `write_html`.

""")
