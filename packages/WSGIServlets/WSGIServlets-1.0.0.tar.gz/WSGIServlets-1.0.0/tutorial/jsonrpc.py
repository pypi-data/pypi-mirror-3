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

class jsonrpc(HTMLPage):
    'Using JSON-RPC with servlets.'

    title = 'JSON-RPC'
    meta = {"pygwt:module" : "/jsonrpc_js/jsonrpc_cli"}

    css = '''
    div#floatbox {
        float: right;
        width: 40%;
        margin: 20px;
        border: solid black 3px;
        padding: 20px;               
    }

    div#quotebox {
        margin-top: 10px;
        border-top: solid black 1px;
    }
    '''

    def write_content(self):
        
        self.writeln(FLOATBOX)
        self.writeln(OVERVIEW)
        self.writeln(SCRIPT)



# -*-*- DOC -*-*-


FLOATBOX = '''
<div id="floatbox">
    Shakespeare Quotes:
    <div id="quotebox">
    </div>
</div>'''

OVERVIEW = make_overview("""

[JSON-RPC](http://groups.google.com/group/json-rpc/web/json-rpc-2-0)
is a remote procecure call protocol using [JSON](http://www.json.org)
for encoding messages between client and server.

This servlet demonstrates communicating with a server that hands out
famous quotes from William Shakespeare's plays and sonnets.  Every
five seconds a new quote is fetched from the server, placed somewhere
randomly in the box to the right and then fades away.  If you view the
web log from running this tutorial you will see repeated POST requests
for URI **/jsonrpc_srv**.


If you view the source of this servlet you will not see much code: all
this servlet does is serve static javascript that was previously
compiled from python source to javascript using the python=>javascript
compiler technology, pyjamas[^1].


The pyjamas application is loaded into the box to the right (a floated
`DIV` element) by loading javascript bootstrap code (which you can see
by viewing the tail end of this source).  It should be made clear that
the client-side of JSON-RPC is NOT provided by WSGIServlets[^2].

This is important to understand: *Only the server-side is provided by
WSGIServlets!*

The server code, in a nutshell, is:


        import random
        from wsgiservlets import JSONRPCServer

        class jsonrpc_srv(JSONRPCServer):

            def rpc_quote(self):
                play = random.choice(PLAYS)
                quote = random.choice(QUOTES[play])
                return quote, play


where `PLAYS` is a list of play/sonnet titles and `QUOTES` is a
mapping of titles to a list of quotes from that play.

You will notice the servlet is an instance of `JSONRPCServer`.  This
is a subclass of `WSGIServlet`.  Any method with prefix `rpc_` is
available to be called by a client (which should call the method
without the `rpc_` prefix, e.g., in this demo, the client is calling
`quote`, not `rpc_quote`).  Any method not prefixed with `rpc_` is NOT
available to clients and becomes a *private* method of the server
implementation.

So, to create a JSON-RPC server with WSGIServlets, subclass
`JSONRPCServer` and create methods with names beginning with `rpc_`.
Your methods can take as input and return as output any python object
that can be translated to JSON.  That's it!



[^1]:
    Discussing pyjamas is beyond the scope of this tutorial.
    Suffice it to say that pyjamas turns traditional web programming
    into something more akin to desktop GUI programming.  Pyjamas
    exposes the DOM to python, thus when the python is compiled to
    javascript and then loaded into a broswer, you discover you can
    manipulate a browser window with python code.  [Check it
    out](http://pyjs.org).

[^2]:

    The author of this tutorial pre-compiled the pyjamas app and
    included the resulting static javascript in the distribution.  The
    original source for the application is also included in the
    distribution (and is well documented for the curious), but
    discussion of client-side JSON-RPC, generally, or pyjamas
    application programming, specifically, is beyond the scope of this
    tutorial.

""")

SCRIPT = '<script language="javascript" src="/jsonrpc_js/bootstrap.js"></script>'
