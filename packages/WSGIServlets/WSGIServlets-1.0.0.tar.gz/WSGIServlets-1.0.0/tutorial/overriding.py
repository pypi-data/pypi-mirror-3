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
from SitePage import *

class overriding(SitePage):

    'How to manage page layout by overriding HTMLPage methods.'

    title = 'Overriding HTMLPage Methods'

    def write_content(self):
        self.writeln(OVERVIEW)



# -*-*- DOC -*-*-


OVERVIEW = make_overview("""
As discussed previously, most servlets will subclass `HTMLPage` and therefore have `write_html` called as part, if not all, of the
response to a request.  Here we will explore this method.

It is implemented, simply, as follows:

        def write_html(self):
            self.write_doctype()
            self.writeln('<HTML>')
            self.write_head()
            self.write_body()
            self.writeln('</HTML>')
            return True

If you are familiar with the HTML specification you will recognize
this method writes a well-formed HTML document: the declaration of the
document type (`<!DOCTYPE...>` element) followed by the opening
`<HTML>` tag; the HEAD element (`<HEAD>...</HEAD>`) followed by the
BODY element (`<BODY>...</BODY>`); lastly, the closing `</HTML>` tag.
You should note the method returns `True` which lets the caller know a
response was generated.

`write_doctype` is fully described in the API reference.

`write_head` calls a series of methods which generate the HEAD element
content.  In turn, the content these methods send to the client is
controlled by the setting of numerous instance variables: `js`, `css`,
`css_links`, etc.  Many have been demonstrated earlier in this
tutorial.  See the API reference for complete details.

`write_body` is where the content is generated.  Between writing the
`<BODY>` and `</BODY>` tags, `write_body` calls `write_body_parts`.
The base implementation of `write_body_parts` is implemented as:

        def write_body_parts(self):
            self.write_content()
    
You may wonder why `write_body` calls `write_body_parts` if the method
only calls `write_content`.  Why not have `write_body` call
`write_content` and be done with it?  Mainly, having a method between
`write_body` and `write_content` makes it much easier to modify page
layout.

For example, imagine a company website with a standard page
layout like this:

    ---------------------------------------------------
    |            |                                    |
    | SIDEBAR    |  CONTENT                           |
    |            |                                    |
    |            |                                    |
    |            |                                    |
    |            |                                    |
    ---------------------------------------------------

This is a fairly common page layout and is easily implemented in
servlets by overriding `write_body_parts` which, in one possible
implementation, can write out a series of DIV elements (along with the
necessary css) and inside the DIV elements, call methods to generate
the output of the sidebar and content; something like this:

    def write_body_parts(self):

        self.writeln('<div id="sidebar">')
        self.write_sidebar()
        self.writeln('</div>')
        self.writeln('<div id="content">')
        self.write_content()
        self.writeln('</div>')

If the above implementation of `write_body_parts` is placed in an
abstract base class (which also has the implementation for
`write_sidebar`) and every servlet in the site inherits from it, then
every page on the site will have the common sidebar.

This is what we have done for this servlet.  It does not inherit from
`HTMLPage` like all the other servlets thus far, but from another
servlet, `SitePage`, which in turn inherits from `HTMLPage`.  If you
view the python source you will see the only method implemented in
this servlet is `write_content`.  `SitePage`, defined in
[SitePage.py](SitePage.py), overrides `write_body_parts` which
generates the DIVs and calls `write_sidebar` and `write_content` in
the appropriate places.  The sidebar for this *site* provides links to
all the tutorials.

The next servlet will demonstrate the ease of modifying page layout
either by modifying the implementation in the abstract base class or
by extending the implementation.

""")
