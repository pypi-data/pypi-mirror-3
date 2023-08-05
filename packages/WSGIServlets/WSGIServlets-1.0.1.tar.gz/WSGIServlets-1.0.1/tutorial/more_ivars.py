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

import random

from TutorialBase import *

class more_ivars(HTMLPage):
    "Further discussion about special attributes."

    def title(self):
        E = '!' * random.randint(1,5)
        return 'More Special Attributes%s' % E

    css_links = ['/more_ivars.css']

    js = """
    function go() {
       alert('Hello, World!');
    }
    """

    shortcut_icon = 'python.ico'

    def write_content(self):
        self.writeln(OVERVIEW)


# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
There are many other attributes you can set in your servlets to
control the generated HTML.  Here are a few, see the reference
documentation for a complete list.

Attribute         | Description
----------------- | --------------------------------------
**css_links**     | In the previous servlet we inserted CSS by setting the `css` attribute.  This created a STYLE element in the HEAD.  You can also refer to CSS in an external document by setting the `css_links` attribute.  The external CSS document refered to by this servlet sets the background color to lightgrey, sets other table border and alignment attributes, and places a border around H1 tags.
**js**            | You can insert javascript by setting the `js` attribute. {button}
**shortcut_icon** | You can specify a shortcut icon by setting this attribute.  For this servlet, I have borrowed the python icon.
**title**         | You have already seen how the title of the document can be set with the `title` attribute.  It can also be callable to generate dynamic titles! Reload this page and watch the title change.

      
""")

OVERVIEW = OVERVIEW.format(button='<button onclick="go()">Click Me!</button>')

