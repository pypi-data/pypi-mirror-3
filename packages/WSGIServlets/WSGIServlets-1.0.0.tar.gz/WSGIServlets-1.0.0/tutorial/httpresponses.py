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

class httpresponses(HTMLPage):

    "How to preemptively return a HTTP status to a client."

    title = "HTTP Responses"
    debug = True
    
    def prep(self):

        # check if the first component of PATH_INFO is a status to
        # raise
        pil = self.path_info_list
        if pil:
            try:
                code = int(pil[0])
            except:
                return

            if code == 400:
                raise HTTPBadRequest
            elif code == 403:
                raise HTTPForbidden('You rotten scoundrel!')
            elif code == 404:
                raise HTTPNotFound('The URL you specified could not be found')
            elif code == 405:
                raise HTTPMethodNotAllowed
            elif code == -2:
                self.debug = False
                raise Exception(DEBUG_EXCEPTION_MSG)
            elif code == -3:
                self.debug = False
                self.gen500msg = '<span style="color:red">' \
                                 'A custom exception message.</span>'
                raise Exception(DEBUG_EXCEPTION_MSG)
            else:
                raise Exception(DEBUG_EXCEPTION_MSG)

    def write_content(self):

        self.writeln(OVERVIEW)

        self.writeln('<ul>')
        
        for code in 400, 403, 404, 405:
            # http_responses_map: status code => HTTPResponse class
            r = http_responses_map[code]
            self.writeln('<li>', LINK.format(code=code, title=r.title))
        
        self.writeln('</ul>')
        


# -*-*- DOC -*-*-



OVERVIEW = make_overview("""
`WSGIServlet` instances use instances of `HTTPResponse` for building
the response to be sent back to the client.  `HTTPResponse` instances
encapsulate the outgoing content as well as the outgoing HTTP headers.

Every incoming request creates an attribute, `response`, which is an
instance of `HTTPOK`, a subclass of `HTTPResponse`.

Calls to `WSGIServlet.write` and `WSGIServlet.writeln` which send
output to the client are actually appending the output to `response`,
which caches all output until it is eventually delivered to the
client.  Likewise, when manipulating outgoing headers (e.g., by
setting cookies, or creating a session), a container for outgoing
headers inside `response` is manipulated.

If your code runs without exception, the content accumulated in
`response` (and all the set headers) will be sent to the client.

If an exception occurs, `repsonse` will be discarded and a new
response will be created, `HTTPInternalServerError`, and returned to
the client.  If the `debug` attribute of the servlet is set to `True`
(it is for this servlet), then the exception stack trace along with
the environment will be sent to the client.  If `debug` is set to
`False` (the default value for servlets unless overridden) then a
terse message controlled by the `gen500msg` attribute will be sent to
the client.

**NOTE: when you click on links in the following examples you will
will raise exceptions which produce error pages.  You will need to use
your browser back button to return to the tutorial!**

This link [will simulate an internal exception](/httpresponses/-1).   
This link [will simulate an internal exception with debug set
to False](/httpresponses/-2).    
This link [will simulate an internal exception with debug set
to False and a custom gen500msg](/httpresponses/-3).

So, how do you return a page to the client other than a HTTP OK
(status 200) or HTTP Internal Server Error (status 500)?  What if you
want to send back a 404 (Not Found), or a 403 (Forbidden) response?
`HTTPResponse` is a subclass of `Exception`, so the answer is simple:
raise an exception with a subclass of `HTTPResponse`.  WSGIServlets
defines a subclass for each status defined in the HTTP 1.1
specification.  See the WSGIServlets reference documentation for a
complete list, but here are examples of a few of the most common (note
how any text you specify in the constructor becomes part of the detail
sent to the client):

""")

LINK = '<A href=/httpresponses/{code}>{title}</A>'
            
DEBUG_EXCEPTION_MSG = """
We're simulating some arbitrary python code exception with the debug
attribute set to True.  When debug is True a stack trace and the
contents of the environment are returned to the client.  When debug is
False, a stark error message is returned (the contents of the
gen500msg attribute).  Setting debug to True while developing your
servlets will prove an invaluable tool.  You'll want to set it to
False for production environments so you don't broadcast your code to
the WWW.
"""
