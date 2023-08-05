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

class environ(HTMLPage):

    "A brief look at self.environ and helper descriptors."

    title = 'Using self.environ'

    def write_content(self):
        self.writeln('Some environment variables for this request:')
        self.writeln('<div class="formoutput">')
        self.writeln('REQUEST_METHOD = ', self.method, BR)
        self.writeln('SCRIPT_NAME = ', self.script_name, BR)
        self.writeln('PATH_INFO = ', self.path_info, BR)
        self.writeln('PATH_INFO as list = ', self.path_info_list, BR)
        self.writeln('QUERY_STRING = ', self.query_string)
        self.writeln('</div>')
        
        self.writeln(make_overview(OVERVIEW.format(sn=self.script_name)))

# -*-*- DOC -*-*-

OVERVIEW = """
The environ parameter passed to the `__call__` method is set as an
attribute of the servlet.  All the standard environment variables as
specified by [PEP 3333](http://www.python.org/dev/peps/pep-3333/) can
be accessed through this attribute, e.g., `self.environ['PATH_INFO']`,
`self.environ['REQUEST_METHOD']`, etc.

As an aid to accessing these variables, a descriptor can be created
with `environ_helper`, which when accessed or set, will act on the
underlying variable in `self.environ`.  The base class, `WSGIServlet`,
creates a number of descriptors for the most commonly accessed
variables:


        class WSGIServlet(object):
            
            method = environ_helper('REQUEST_METHOD')
            script_name = environ_helper('SCRIPT_NAME')
            path_info = environ_helper('PATH_INFO')
            query_string = environ_helper('QUERY_STRING')
            ...


You can add `environ_helper` attributes to your own servlets for
environment variables you commonly use in your application.

As a further convenience, a read-only data descriptor,
`path_info_list`, returns the value of PATH_INFO, preprocessed and
returned as a list, splitting on "/" and skipping any component
elements that are all whitespace or ".".  This can be an invaluable
tool for applications that use components of PATH_INFO as a series of
keys in processing the request.

Try these links to see the values change above (or write your own url
in your browser location bar):
    

"""

for link in ('/this/is/a/test',
             '/this/  //.///is/a/test',
             '?some=query&string=',
             '/some/path/plus?query=string&a=b&c=d',
             ):

    OVERVIEW += '  * [{sn}' + link + ']({sn}' + link + ')\n'
    
