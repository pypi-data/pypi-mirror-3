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

users = {'wsgi' : 'servlets'}

class auth2(HTMLPage):
      'Basic HTTP authentication, Part II.'

      title = 'Basic HTTP Authentication (2 of 2)'

      auth_realm = 'WSGI Servlet Auth Tutorial'

      def prep(self):
            self.auth_with_mapping(users)

      def write_content(self):

            self.writeln(OVERVIEW)



# -*-*- DOC -*-*-


OVERVIEW = make_overview("""
WSGIServlets provides three methods and a data attribute for
implementing [Basic HTTP
Authentication](http://www.ietf.org/rfc/rfc2617.txt):

  * `WSGIServlet.get_basic_auth()`

    Searches the incoming HTTP headers for the `Authorization` header
    and if found, returns a tuple: (*username*, *password*).  If the
    header is found but the username and password cannot be decoded,
    the method does not return and a HTTP Bad Request is sent to the
    client.  If the header is not found, `unauthorized` is called.
   

    
  * `WSGIServlet.unauthorized()`

    Creates a HTTP Unauthorized response, setting the HTTP header
    `WWW-Authenticate` to the contents of the `auth_realm` attribute.
    The response is sent directly to the client and the method does
    not return to the caller.

  * `WSGIServlet.auth_realm`

    A string used by `unauthorized()` to specify the realm for the
    authentication and will be presented to users by browsers when
    prompting for a username and password.  This servlet sets
    `auth_realm` to **WSGI Servlet Auth Tutorial**.

  * `WSGIServlet.auth_with_mapping()`

    A helper method that calls `get_basic_auth` and checks if the
    returned username and password are non-empty and exist in the
    mapping passed in to the call.  The mapping's keys are usernames
    and values are their associated passwords.  Any mapping
    implementing the standard `dict.get` method can be used.  This
    servlet uses this method and passes in a mapping: `{'wsgi' :
    'servlets'}`.


Something to note in the code of this servlet: the call to
`auth_with_mapping` is made in the `prep` method which is called by
`_lifecycle` before `write_html`.  This demonstrates placing certain
kinds of logic outside of content generation.  Also consider we could
have placed this call inside an abstract base class:

                WSGIServlet
                  |
                  |--HTMLPage
                       |
                       |--SitePage
                            |
                            |--AuthorizedSitePage


With `AuthorizedSitePage` implemented, in its entirety, as follows:


                class AuthorizedSitePage(SitePage):

                      def prep(self):

                            self.auth_with_mapping(SOME_MAPPING)
                            SitePage.prep(self)


If `SitePage` is an abstract base class implementing the basic layout
of your site, then all servlets inherititing from `SitePage` will
require no authentication while servlets inheriting from
`AuthorizedSitePage` will require authentication.
""")


