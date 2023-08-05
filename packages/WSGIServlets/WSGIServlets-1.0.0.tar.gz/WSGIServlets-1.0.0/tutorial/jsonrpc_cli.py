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

"""
This is a pyjamas app (client side) to demonstrate JSON-RPC for the
tutorial.

See jsonrpc.py for the WSGIServlet that loads this client in a
right-floated DIV.

See jsonrpc_srv.py for the JSONRPCServer (a WSGIServlet subclass) that
acts as the JSON-RPC server.

This file needs to be compiled and linked with pyjamas:

    pyjsbuild --output jsonrpc_js jsonrpc_cli.py

THIS IS ALREADY DONE as part of the WSGIServlets distribution, so you
do not need pyjamas to run this tutorial, but if you want to tweak
this example and recompile, you will need pyjamas.

Check it out:  http://pyjs.org/

"""

from pyjamas import DOM
from pyjamas import Window
from pyjamas.ui.HTML import HTML
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.AbsolutePanel import AbsolutePanel
from pyjamas.Timer import Timer
from pyjamas.JSONService import JSONProxy

import random

FADE = 5000.0/256  # fade out every 5 seconds
DIVID = 'quotebox' # the DIV to put this app inside

class jsonrpc_cli:

    def __init__(self):

        # set up rpc
        self.remote = JSONProxy('/jsonrpc_srv', ['quote'])

        # create panel
        self.panel = panel = AbsolutePanel(StyleName='quotes')

        # get the underlying DIV element
        quotebox = DOM.getElementById(DIVID)

        # get the DIV's width and set height proportionally
        width = quotebox.clientWidth
        self.w, self.h = width, width/2
        panel.setSize('%dpx' % self.w, '%dpx' % self.h)

        # add the panel to the DIV and start it up
        RootPanel(DIVID).add(panel)
        self.setup()
        
    def setup(self):

        # fetch a quote.  The response from the server will be handled
        # by onRemoteResponse()
        self.remote.quote(self)

    def onRemoteResponse(self, response, request_info):
        'Called on repsonse from jsonrpc call'

        # Get the quote and play
        quote, play = response

        # pick a random place
        left = random.random() * self.w * .25
        top =  random.random() * self.h * .5

        # Generate HTML
        self.hw = HTML("<h3>%s<br><em>%s</em></h3>" % (quote, play))

        # add it...reset the color and set the timer
        self.panel.add(self.hw, left, top)
        self.color = 0
        self.timer = Timer(FADE, self)


    def onRemoteError(self, error_code, error, request_info):
        'Called when a jsonrpc call generated an error'

        # popup the error
        Window.alert('Error code: %d\n\n\n%s' % (error_code, error['message']))
        

    def onTimer(self, tid):
        '''Called when timer goes off.

        Either: fade the color of the text -or- if totally faded,
        remove the current quote and setup another fetch.

        '''

        # timer has gone off...fade the color
        self.color += 1
        colors = '#' + ('%02x' % self.color)*3
        DOM.setStyleAttribute(self.hw.getElement(), 'color', colors)

        # either reset the timer or, if we've faded to oblivion,
        # remove it and start over
        if self.color < 255:
            self.timer = Timer(FADE, self)
        else:
            self.panel.remove(self.hw)
            self.setup()


if __name__ == '__main__':
    jsonrpc_cli()
    
